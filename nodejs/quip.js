/*
 * Copyright 2014 Quip
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

const https = require('https')
const http = require('http')
const querystring = require('querystring')
const url = require('url')
const WebSocket = require('ws')
const request = require('request')

const isProd = process.env.NODE_ENV === 'production'
const baseURI = isProd ? 'platform.quip.com' : 'platform.docker.qa'
const baseURL = isProd ? `https://${baseURI}` : `http://${baseURI}`
const basePort = process.env.NODE_ENV === 'production' ? 443 : 10000
const httpLib = isProd ? https : http

/**
 * Folder colors
 * @enum {number}
 */
const Color = {
  MANILA: 0,
  RED: 1,
  ORANGE: 2,
  GREEN: 3,
  BLUE: 4,
}

/**
 * Edit operations
 * @enum {number}
 */
const Operation = {
  APPEND: 0,
  PREPEND: 1,
  AFTER_SECTION: 2,
  BEFORE_SECTION: 3,
  REPLACE_SECTION: 4,
  DELETE_SECTION: 5,
}

/**
 * A Quip API client.
 *
 * To make API calls that access Quip data, initialize with an accessToken.
 *
 *    const quip = require('quip');
 *    const client = quip.Client({accessToken: '...'});
 *    const user = await client.getAuthenticatedUser();
 *
 * To generate authorization URLs, i.e., to implement OAuth login, initialize
 * with a clientId and and clientSecret.
 *
 *    const quip = require('quip');
 *    const client = quip.Client({clientId: '...', clientSecret: '...'});
 *    response.writeHead(302, {
 *      'Location': client.getAuthorizationUrl()
 *    });
 *
 * @param {{accessToken: (string|undefined),
 *          clientId: (string|undefined),
 *          clientSecret: (string|undefined)}} options
 * @constructor
 */
function Client(options) {
  this.accessToken = options.accessToken
  this.clientId = options.clientId
  this.clientSecret = options.clientSecret
}

/**
 * Returns the URL the user should be redirected to to sign in.
 *
 * @param {string} redirectUri
 * @param {string=} state
 */
Client.prototype.getAuthorizationUrl = function(redirectUri, state) {
  return (
    `${baseURL}:${basePort}/1/oauth/login?` +
    querystring.stringify({
      redirect_uri: redirectUri,
      state: state,
      response_type: 'code',
      client_id: this.clientId,
    })
  )
}

/**
 * Exchanges a verification code for an access_token.
 *
 * Once the user is redirected back to your server from the URL
 * returned by `getAuthorizationUrl`, you can exchange the `code`
 * argument for an access token with this method.
 *
 * @param {string} redirectUri
 * @param {string} code
 * @return {Promise}
 */
Client.prototype.getAccessToken = function(redirectUri, code) {
  return this.call_(
    'oauth/access_token?' +
      querystring.stringify({
        redirect_uri: redirectUri,
        code: code,
        grant_type: 'authorization_code',
        client_id: this.clientId,
        client_secret: this.clientSecret,
      }),
  )
}

/**
 * @return {Promise}
 */
Client.prototype.getAuthenticatedUser = function() {
  return this.call_('users/current')
}

/**
 * @param {string} id
 * @return {Promise}
 */
Client.prototype.getUser = async function(id) {
  const users = await this.getUsers([id])
  return users[id]
}

/**
 * @param {Array.<string>} ids
 * @return {Promise}
 */
Client.prototype.getUsers = function(ids) {
  return this.call_(
    'users/?' +
      querystring.stringify({
        ids: ids.join(','),
      }),
  )
}

/**
 * @return {Promise}
 */
Client.prototype.getContacts = function() {
  return this.call_('users/contacts')
}

/**
 * @param {string} id
 * @return {Promise}
 */
Client.prototype.getFolder = async function(id) {
  const folders = await this.getFolders([id])
  return folders[id]
}

/**
 * @param {Array.<string>} ids
 * @return {Promise}
 */
Client.prototype.getFolders = function(ids) {
  return this.call_(
    'folders/?' +
      querystring.stringify({
        ids: ids.join(','),
      }),
  )
}

/**
 * @param {{title: string,
 *          parentId: (string|undefined),
 *          color: (Color|undefined),
 *          memberIds: (Array.<string>|undefined)}} options
 * @return {Promise}
 */
Client.prototype.newFolder = function(options) {
  const args = {
    title: options.title,
    parent_id: options.parentId,
    color: options.color,
  }
  if (options.memberIds) {
    args['member_ids'] = options.memberIds.join(',')
  }
  return this.call_('folders/new', args)
}

/**
 * @param {{folderId: string,
 *          title: (string|undefined),
 *          color: (Color|undefined)}} options
 * @return {Promise}
 */
Client.prototype.updateFolder = function(options) {
  const args = {
    folder_id: options.folderId,
    title: options.title,
    color: options.color,
  }
  return this.call_('folders/update', args)
}

/**
 * @param {{folderId: string,
 *          memberIds: Array.<string>}} options
 * @return {Promise}
 */
Client.prototype.addFolderMembers = function(options) {
  const args = {
    folder_id: options.folderId,
    member_ids: options.memberIds.join(','),
  }
  return this.call_('folders/add-members', args)
}

/**
 * @param {{folderId: string,
 *          memberIds: Array.<string>}} options
 * @return {Promise}
 */
Client.prototype.removeFolderMembers = function(options) {
  const args = {
    folder_id: options.folderId,
    member_ids: options.memberIds.join(','),
  }
  return this.call_('folders/remove-members', args)
}

/**
 * @param {{threadId: string,
 *          maxUpdatedUsec: (number|undefined),
 *          count: (number|undefined)}} options
 * @return {Promise}
 */
Client.prototype.getMessages = function(options) {
  return this.call_(
    'messages/' +
      options.threadId +
      '?' +
      querystring.stringify({
        max_updated_usec: options.maxUpdatedUsec,
        count: options.count,
      }),
  )
}

/**
 * @param {{threadId: string,
 *          content: string,
 *          silent: (boolean|undefined)}} options
 * @return {Promise}
 */
Client.prototype.newMessage = function(options) {
  const args = {
    thread_id: options.threadId,
    frame: options.frame,
    content: options.content,
    parts: options.parts,
    attachments: options.attachments,
    silent: options.silent ? 1 : undefined,
    annotation_id: options.annotationId,
    section_id: options.sectionId,
    suggested_responses: options.suggestedResponses,
  }
  return this.call_('messages/new', args)
}

/**
 * @param {string} id
 * @return {Promise}
 */
Client.prototype.getThread = async function(id) {
  const threads = await this.getThreads([id])
  return threads[id]
}

/**
 * @param {Array.<string>} ids
 * @return {Promise}
 */
Client.prototype.getThreads = function(ids) {
  return this.call_(
    'threads/?' +
      querystring.stringify({
        ids: ids.join(','),
      }),
  )
}

/**
 * @param {{maxUpdatedUsec: (number|undefined),
 *          count: (number|undefined)}?} options
 * @return {Promise}
 */
Client.prototype.getRecentThreads = function(options) {
  return this.call_(
    'threads/recent?' +
      querystring.stringify(
        options
          ? {
              max_updated_usec: options.maxUpdatedUsec,
              count: options.count,
            }
          : {},
      ),
  )
}

/**
 * @param {{content: string,
 *          title: (string|undefined),
 *          format: (string|undefined),
 *          memberIds: (Array.<string>|undefined)}} options
 * @return {Promise}
 */
Client.prototype.newDocument = function(options) {
  const args = {
    content: options.content,
    title: options.title,
    format: options.format,
  }
  if (options.memberIds) {
    args['member_ids'] = options.memberIds.join(',')
  }
  return this.call_('threads/new-document', args)
}

/**
 * @param {{threadId: string,
 *          content: string,
 *          operation: (Operation|undefined),
 *          format: (string|undefined),
 *          sectionId: (string|undefined)}} options
 * @return {Promise}
 */
Client.prototype.editDocument = function(options) {
  const args = {
    thread_id: options.threadId,
    content: options.content,
    location: options.operation,
    format: options.format,
    section_id: options.sectionId,
  }
  return this.call_('threads/edit-document', args)
}

/**
 * @param {{threadId: string,
 *          memberIds: Array.<string>}} options
 * @return {Promise}
 */
Client.prototype.addThreadMembers = function(options) {
  const args = {
    thread_id: options.threadId,
    member_ids: options.memberIds.join(','),
  }
  return this.call_('threads/add-members', args)
}

/**
 * @param {{threadId: string,
 *          memberIds: Array.<string>}} options
 * @return {Promise}
 */
Client.prototype.removeThreadMembers = function(options) {
  const args = {
    thread_id: options.threadId,
    member_ids: options.memberIds.join(','),
  }
  return this.call_('threads/remove-members', args)
}

/**
 * @param {{url: string,
 *          threadId: string}} options
 * @return {Promise}
 */
Client.prototype.addBlobFromURL = async function(options) {
  return this.call_(`blob/${options.threadId}`, {
    blob: request(options.url),
  })
}

/**
 * @param {{path: string,
 *          threadId: string}} options
 * @return {Promise}
 */
Client.prototype.addBlobFromPath = async function(options) {
  return this.call_(`blob/${options.threadId}`, {
    blob: fs.createReadStream(options.path),
  })
}

/**
 * @return {Promise<WebSocket>}
 */
Client.prototype.connectWebsocket = function() {
  return this.call_('websockets/new').then(newSocket => {
    if (!newSocket || !newSocket.url) {
      throw new Error(newSocket ? newSocket.error : 'Request failed')
    }
    const urlInfo = url.parse(newSocket.url)
    const ws = new WebSocket(newSocket.url, {
      origin: `${urlInfo.protocol}//${urlInfo.hostname}`,
    })
    return ws
  })
}

/**
 * @param {string} path
 * @param {Object.<string, *>=} postArguments
 * @return {Promise}
 */
Client.prototype.call_ = function(path, postArguments) {
  const requestOptions = {
    uri: `${baseURL}:${basePort}/1/${path}`,
    headers: {},
  }
  if (this.accessToken) {
    requestOptions.headers['Authorization'] = 'Bearer ' + this.accessToken
  }
  if (postArguments) {
    const formData = {}
    for (let name in postArguments) {
      if (postArguments[name]) {
        formData[name] = postArguments[name]
      }
    }
    requestOptions.method = 'POST'
    requestOptions.formData = formData
  } else {
    requestOptions.method = 'GET'
  }
  return new Promise((resolve, reject) => {
    const callback = (err, res, body) => {
      if (err) {
        return reject(err)
      }
      let responseObject = null
      try {
        responseObject = /** @type {Object} */ (JSON.parse(body))
      } catch (err) {
        reject(`Invalid response for ${path}: ${body}`)
        return
      }
      if (res.statusCode !== 200) {
        reject(new ClientError(res, responseObject))
      } else {
        resolve(responseObject)
      }
    }
    request(requestOptions, callback)
  })
}

/**
 * @param {http.IncomingMessage} httpResponse
 * @param {Object} info
 * @extends {Error}
 * @constructor
 */
function ClientError(httpResponse, info) {
  this.httpResponse = httpResponse
  this.info = info
}
ClientError.prototype = Object.create(Error.prototype)

exports.Color = Color
exports.Operation = Operation
exports.Client = Client
exports.ClientError = ClientError

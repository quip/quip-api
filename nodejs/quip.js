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

var https = require('https');
var querystring = require('querystring');

/**
 * Folder colors
 * @enum {number}
 */
var Color = {
    MANILA: 0,
    RED: 1,
    ORANGE: 2,
    GREEN: 3,
    BLUE: 4
};

/**
 * Edit operations
 * @enum {number}
 */
var Operation = {
    APPEND: 0,
    PREPEND: 1,
    AFTER_SECTION: 2,
    BEFORE_SECTION: 3,
    REPLACE_SECTION: 4,
    DELETE_SECTION: 5
};

/**
 * A Quip API client.
 *
 * To make API calls that access Quip data, initialize with an accessToken.
 *
 *    var quip = require('quip');
 *    var client = quip.Client({accessToken: '...'});
 *    client.getAuthenticatedUser(function();
 *
 * To generate authorization URLs, i.e., to implement OAuth login, initialize
 * with a clientId and and clientSecret.
 *
 *    var quip = require('quip');
 *    var client = quip.Client({clientId: '...', clientSecret: '...'});
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
    this.accessToken = options.accessToken;
    this.clientId = options.clientId;
    this.clientSecret = options.clientSecret;
}

/**
 * Returns the URL the user should be redirected to to sign in.
 *
 * @param {string} redirectUri
 * @param {string=} state
 */
Client.prototype.getAuthorizationUrl = function(redirectUri, state) {
    return 'https://platform.quip.com/1/oauth/login?' + querystring.stringify({
        'redirect_uri': redirectUri,
        'state': state,
        'response_type': 'code',
        'client_id': this.clientId
    });
};

/**
 * Exchanges a verification code for an access_token.
 *
 * Once the user is redirected back to your server from the URL
 * returned by `getAuthorizationUrl`, you can exchange the `code`
 * argument for an access token with this method.
 *
 * @param {string} redirectUri
 * @param {string} code
 * @param {function(Error, Object)} callback
 */
Client.prototype.getAccessToken = function(redirectUri, code, callback) {
    this.call_('oauth/access_token?' + querystring.stringify({
        'redirect_uri': redirectUri,
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': this.clientId,
        'client_secret': this.clientSecret
    }), callback);
};

/**
 * @param {function(Error, Object)} callback
 */
Client.prototype.getAuthenticatedUser = function(callback) {
    this.call_('users/current', callback);
};

/**
 * @param {string} id
 * @param {function(Error, Object)} callback
 */
Client.prototype.getUser = function(id, callback) {
    this.getUsers([id], function(err, users) {
        callback(err, err ? null : users[id]);
    });
};

/**
 * @param {Array.<string>} ids
 * @param {function(Error, Object)} callback
 */
Client.prototype.getUsers = function(ids, callback) {
    this.call_('users/?' + querystring.stringify({
        'ids': ids.join(',')
    }), callback);
};

/**
 * @param {function(Error, Object)} callback
 */
Client.prototype.getContacts = function(callback) {
    this.call_('users/contacts', callback);
};

/**
 * @param {string} id
 * @param {function(Error, Object)} callback
 */
Client.prototype.getFolder = function(id, callback) {
    this.getFolders([id], function(err, folders) {
        callback(err, err ? null : folders[id]);
    });
};

/**
 * @param {Array.<string>} ids
 * @param {function(Error, Object)} callback
 */
Client.prototype.getFolders = function(ids, callback) {
    this.call_('folders/?' + querystring.stringify({
        'ids': ids.join(',')
    }), callback);
};

/**
 * @param {{title: string,
 *          parentId: (string|undefined),
 *          color: (Color|undefined),
 *          memberIds: (Array.<string>|undefined)}} options
 * @param {function(Error, Object)} callback
 */
Client.prototype.newFolder = function(options, callback) {
    var args = {
        'title': options.title,
        'parent_id': options.parentId,
        'color': options.color
    };
    if (options.memberIds) {
        args['member_ids'] = options.memberIds.join(',');
    }
    this.call_('folders/new', callback, args);
};

/**
 * @param {{folderId: string,
 *          title: (string|undefined),
 *          color: (Color|undefined)}} options
 * @param {function(Error, Object)} callback
 */
Client.prototype.updateFolder = function(options, callback) {
    var args = {
        'folder_id': options.folderId,
        'title': options.title,
        'color': options.color
    };
    this.call_('folders/update', callback, args);
};

/**
 * @param {{folderId: string,
 *          memberIds: Array.<string>}} options
 * @param {function(Error, Object)} callback
 */
Client.prototype.addFolderMembers = function(options, callback) {
    var args = {
        'folder_id': options.folderId,
        'member_ids': options.memberIds.join(',')
    };
    this.call_('folders/add-members', callback, args);
};

/**
 * @param {{folderId: string,
 *          memberIds: Array.<string>}} options
 * @param {function(Error, Object)} callback
 */
Client.prototype.removeFolderMembers = function(options, callback) {
    var args = {
        'folder_id': options.folderId,
        'member_ids': options.memberIds.join(',')
    };
    this.call_('folders/remove-members', callback, args);
};

/**
 * @param {{threadId: string,
 *          maxUpdatedUsec: (number|undefined),
 *          count: (number|undefined)}} options
 * @param {function(Error, Object)} callback
 */
Client.prototype.getMessages = function(options, callback) {
    this.call_('messages/' + options.threadId + '?' + querystring.stringify({
        'max_updated_usec': options.maxUpdatedUsec,
        'count': options.count
    }), callback);
};

/**
 * @param {{threadId: string,
 *          content: string,
 *          silent: (number|undefined)}} options
 * @param {function(Error, Object)} callback
 */
Client.prototype.newMessage = function(options, callback) {
    var args = {
        'thread_id': options.threadId,
        'content': options.content,
        'silent': (options.silent ? 1 : undefined)
    };
    this.call_('messages/new', callback, args);
};

/**
 * @param {string} id
 * @param {function(Error, Object)} callback
 */
Client.prototype.getThread = function(id, callback) {
    this.getThreads([id], function(err, threads) {
        callback(err, err ? null : threads[id]);
    });
};

/**
 * @param {Array.<string>} ids
 * @param {function(Error, Object)} callback
 */
Client.prototype.getThreads = function(ids, callback) {
    this.call_('threads/?' + querystring.stringify({
        'ids': ids.join(',')
    }), callback);
};

/**
 * @param {{maxUpdatedUsec: (number|undefined),
 *          count: (number|undefined)}?} options
 * @param {function(Error, Object)} callback
 */
Client.prototype.getRecentThreads = function(options, callback) {
    this.call_('threads/recent?' + querystring.stringify(options ? {
        'max_updated_usec': options.maxUpdatedUsec,
        'count': options.count
    } : {}), callback);
};

/**
 * @param {{content: string,
 *          title: (string|undefined),
 *          format: (string|undefined),
 *          memberIds: (Array.<string>|undefined)}} options
 */
Client.prototype.newDocument = function(options, callback) {
    var args = {
        'content': options.content,
        'title': options.title,
        'format': options.format
    };
    if (options.memberIds) {
        args['member_ids'] = options.memberIds.join(',');
    }
    this.call_('threads/new-document', callback, args);
};

/**
 * @param {{threadId: string,
 *          content: string,
 *          operation: (Operation|undefined),
 *          format: (string|undefined),
 *          sectionId: (string|undefined)}} options
 */
Client.prototype.editDocument = function(options, callback) {
    var args = {
        'thread_id': options.threadId,
        'content': options.content,
        'location': options.operation,
        'format': options.format,
        'section_id': options.sectionId
    };
    this.call_('threads/edit-document', callback, args);
};

/**
 * @param {{threadId: string,
 *          memberIds: Array.<string>}} options
 * @param {function(Error, Object)} callback
 */
Client.prototype.addThreadMembers = function(options, callback) {
    var args = {
        'thread_id': options.threadId,
        'member_ids': options.memberIds.join(',')
    };
    this.call_('threads/add-members', callback, args);
};

/**
 * @param {{threadId: string,
 *          memberIds: Array.<string>}} options
 * @param {function(Error, Object)} callback
 */
Client.prototype.removeThreadMembers = function(options, callback) {
    var args = {
        'thread_id': options.threadId,
        'member_ids': options.memberIds.join(',')
    };
    this.call_('threads/remove-members', callback, args);
};

/**
 * @param {string} path
 * @param {function(Error, Object)} callback
 * @param {Object.<string, *>=} postArguments
 */
Client.prototype.call_ = function(path, callback, postArguments) {
    var requestOptions = {
        hostname: 'platform.quip.com',
        port: 443,
        path: '/1/' + path,
        headers: {}
    };
    if (this.accessToken) {
        requestOptions.headers['Authorization'] = 'Bearer ' + this.accessToken;
    }
    var requestBody = null;
    if (postArguments) {
        for (var name in postArguments) {
            if (!postArguments[name]) {
                delete postArguments[name];
            }
        }
        requestOptions.method = 'POST';
        requestBody = querystring.stringify(postArguments);
        requestOptions.headers['Content-Type'] =
            'application/x-www-form-urlencoded';
        requestOptions.headers['Content-Length'] =
            Buffer.byteLength(requestBody);
    } else {
        requestOptions.method = 'GET';
    }
    var request = https.request(requestOptions, function(response) {
        var data = [];
        response.on('data', function(chunk) {
            data.push(chunk);
        });
        response.on('end', function() {
            var responseObject = null;
            try {
                responseObject = /** @type {Object} */(
                    JSON.parse(data.join('')));
            } catch (err) {
                callback(err, null);
                return;
            }
            if (response.statusCode != 200) {
                callback(new ClientError(response, responseObject), null);
            } else {
                callback(null, responseObject);
            }
        });
    });
    request.on('error', function(error) {
        callback(error, null);
    });
    if (requestBody) {
        request.write(requestBody);
    }
    request.end();
};

/**
 * @param {http.IncomingMessage} httpResponse
 * @param {Object} info
 * @extends {Error}
 * @constructor
 */
function ClientError(httpResponse, info) {
    this.httpResponse = httpResponse;
    this.info = info;
}
ClientError.prototype = Object.create(Error.prototype);

exports.Color = Color;
exports.Operation = Operation;
exports.Client = Client;
exports.ClientError = ClientError;

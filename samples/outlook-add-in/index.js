var fs = require('fs');
var bodyParser = require('body-parser');
var async = require('async');
var express = require('express');
var quip = require('./quip');
var config = require('./config.json');

var app = express();

app.set('port', (process.env.PORT || 5000));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use(express.static('QuipIt', {
  index: false
}));

app.post('/quip-it', function(request, response) {
    var userEmail = request.body.userEmail;
    var accessToken = config.accessTokens[userEmail];
    if (!accessToken) {
      console.error("No access token for ", userEmail);
      return;
    }
    var fromEmail = request.body.from;
    var toEmails = request.body.to;
    var subject = request.body.subject;
    var body = request.body.body;
    var client = new quip.Client({accessToken: accessToken});
    async.waterfall([
      client.getContacts.bind(client),
      function createNewDocument(contacts, callback) {
        var memberIds = [];
        contacts.forEach(function(contact) {
          if (contact.emails.some(function(email) {
            return email == fromEmail || toEmails.indexOf(email) >= 0;
          })) {
            memberIds.push(contact.id);
          }
        });
        client.newDocument({
            content: body,
            title: subject,
            format: "markdown",
            memberIds: memberIds
        }, callback);
      },
      function addMessage(result, callback) {
        var content = [
          "Created from an email from", fromEmail, "to", toEmails.join(", "),
          "in Outlook"
        ].join(" ");
        client.newMessage({
          threadId: result.thread.id,
          content: content
        }, callback.bind(null, result));
      }
    ], function(error, result) {
      if (error) {
        response.send({error: error});
      } else {
        response.send(result);
      }
    });
});

app.listen(app.get('port'), function() {
  console.log('Running on port', app.get('port'));
});

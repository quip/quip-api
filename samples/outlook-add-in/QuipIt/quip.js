/// <reference path="../App.js" />

(function () {
  "use strict";

  Office.initialize = function(reason) {
      $(document).ready(quipIt);
  };

  function extractEmails(emails) {
    return Object.keys(emails.reduce(function(map, address) {
      map[address.emailAddress.toLowerCase()] = address.displayName;
      return map
    }, {}));
  }
  function quipIt() {
    var mailbox = Office.context.mailbox;
    var item = mailbox.item;
    if (item.itemType != Office.MailboxEnums.ItemType.Message) {
      return;
    }

    var subject = item.subject;
    var userEmail = mailbox.userProfile.emailAddress;
    item.body.getAsync('html', function(result){
      var $status = $(".quip-status");
      if (result.status === 'succeeded') {
        $.post("/quip-it", {
          userEmail: userEmail,
          from: extractEmails([item.from])[0],
          to: extractEmails(item.to.concat(item.cc)),
          subject: subject,
          body: result.value
        }, function(response) {
          $status.hide();
          if (response.thread) {
            $(".quip-open-thread").attr("href", response.thread.link).show();
          }
        }).fail(function() {
          $status.text("Something went wrong. :(");
        });
      } else {
        $status.text("Error " + result);
      }
    });

    item.body.getAsync('text', function(result){
      if (result.status === 'succeeded') {
        console.log(result);
      }
    });
  }
})();

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

var serviceNames = [];
var selectedServiceName = "";
var serviceButtons = document.querySelectorAll(".services li button");
for (var i = 0; i < serviceButtons.length; i++) {
    var serviceButton = serviceButtons[i];
    var serviceName = serviceButton.className;
    serviceNames.push(serviceName);
    serviceButton.onclick = selectService.bind(this, serviceName);
}

document.querySelector("#api-token").oninput = updateHookUrl;
document.querySelector("#thread-id").oninput = updateHookUrl;

updateHookUrl();

function selectService(serviceName) {
    for (var i = 0; i < serviceNames.length; i++) {
        if (serviceNames[i] == serviceName) {
            document.body.classList.add(serviceNames[i]);
        } else {
            document.body.classList.remove(serviceNames[i]);
        }
    }
    selectedServiceName = serviceName;
    updateHookUrl();
}

function updateHookUrl() {
    var apiToken = document.querySelector("#api-token").value;
    var threadId = document.querySelector("#thread-id").value;
    var urlNode = document.querySelector("#hook-url");
    if (!apiToken || !threadId || !selectedServiceName) {
        urlNode.value = "Complete the steps above...";
        urlNode.classList.add("disabled");
        return;
    }

    urlNode.value = location.protocol + "//" + location.hostname +
        "/hook?service=" + encodeURIComponent(selectedServiceName) +
        "&thread_id=" + encodeURIComponent(threadId) +
        "&api_token=" + encodeURIComponent(apiToken);
    urlNode.classList.remove("disabled");
    urlNode.select();
}

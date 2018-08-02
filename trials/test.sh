#!/bin/bash

# request user (token owner): dwillhite@quip.com: dKWAEApvV4V
# quip.com: FTGAcAzRzdg
# files, JiraTest: ba4yA6bgL0fD, Things: WBAcArDaZGYD
set -x 

# this is api key, should work for root apis
at='ZEtXQU1BVmJjQkg=|1563288140|zwmDQ60jcM8k0R7kmJ/pAROsNaAOrCcp/meLucdIOBg='

curl http://platform.docker.qa:10000/1/threads/recent -H "Authorization: Bearer $at" | python -m json.tool # TESTED
curl http://platform.docker.qa:10000/1/threads/ba4yA6bgL0fD -H "Authorization: Bearer $at" | python -m json.tool # TESTED

# curl http://platform.docker.qa:10000/1/oauth/login -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/oauth/access_token -H "Authorization: Bearer $at" | python -m json.tool
curl 'http://platform.docker.qa:10000/1/oauth/access_token' -d "grant_type=refresh_token&refresh_token=$ert&client_id=FTGAcAzRzdg-ce14b24e386e410ca0f21fa54e17c2bd&client_secret=7c8f4b2dbb124c66a682b4dedb607f09"
curl -s 'http://platform.docker.qa:10000/1/oauth/revoke?' -d "token=$rt&client_id=FTGAcAzRzdg-ce14b24e386e410ca0f21fa54e17c2bd&client_secret=7c8f4b2dbb124c66a682b4dedb607f09"
curl http://platform.docker.qa:10000/1/users/current -H "Authorization: Bearer $at" | python -m json.tool # TESTED
curl http://platform.docker.qa:10000/1/users/contacts -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/users/BREAEAINALE -H "Authorization: Bearer $at" | python -m json.tool # TESTED
curl http://platform.docker.qa:10000/1/users/brina@quip.com -H "Authorization: Bearer $at" | python -m json.tool # TESTED
curl http://platform.docker.qa:10000/1/users/?ids=dKWAEApvV4V,BREAEAINALE -H "Authorization: Bearer $at" | python -m json.tool # TESTED
# curl http://platform.docker.qa:10000/1/users/update -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/folders/UQNAOAMwq9d -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/folders/?ids=JAZAOAXMKK7,LLYAOA0KAUV -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/folders/new -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/folders/update -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/folders/add-members -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/folders/remove-members -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/teams/current -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/threads/recent -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/threads/new-document -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/threads/new-chat -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/threads/edit-document -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/threads/add-members -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/threads/remove-members -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/threads/pin-to-desktop -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/threads/search/ -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/threads/WBAcArDaZGYD -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/threads/?ids=KUfAAAacN4b,KJDAAA8hnTx -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/messages/KUfAAAacN4b -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/messages/new -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/blob/JcUAAAls35b/E8PFroUvsmXaby5WiJ1tcA -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/blob/KUfAAAacN4b -H "Authorization: Bearer $at" | python -m json.tool
curl -F 'blob=@/Users/dwillhite/Desktop/images/soccer-ball.jpeg' 'http://platform.docker.qa:10000/1/blob/WIdAAANyW8q' -H "Authorization: Bearer $pat"
# curl http://platform.docker.qa:10000/1/websockets/new -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/integrations/new -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/integrations/refresh -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/integrations/create -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/integrations/update -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/integrations/delete -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/integrations/ping -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/integrations/verify_code -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/integrations/twitter -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/integrations/email -H "Authorization: Bearer $at" | python -m json.tool

# curl http://platform.docker.qa:10000/1/admin/threads/list -H "Authorization: Bearer $at" | python -m json.tool  ## can't execute because of bigquery
# curl http://platform.docker.qa:10000/1/admin/threads/search -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/admin/threads/([a-zA-Z0-9:/]{11,12}) -H "Authorization: Bearer $at" | python -m json.tool  # Tested
# curl http://platform.docker.qa:10000/1/admin/messages/([a-zA-Z0-9]{11,12}) -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/admin/threads/add-members -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/admin/threads/remove-members -H "Authorization: Bearer $at" | python -m json.tool
curl 'http://platform.docker.qa:10000/1/admin/threads/?ids=ba4yA6bgL0fD,WBAcArDaZGYD&company_id=FTGAcAzRzdg' -H "Authorization: Bearer $at" | python -m json.tool # TESTED
curl http://platform.docker.qa:10000/1/admin/users/list -X POST -H "Authorization: Bearer $at" -d "company_id=FTGAcAzRzdg" | python -m json.tool
curl http://platform.docker.qa:10000/1/admin/users/BREAEAINALE?company_id=FTGAcAzRzdg -H "Authorization: Bearer $at" | python -m json.tool
curl http://platform.docker.qa:10000/1/admin/users/brina@quip.com?company_id=FTGAcAzRzdg -H "Authorization: Bearer $at" | python -m json.tool ## doesn't work, i believe extra auth requires real user_id
# curl http://platform.docker.qa:10000/1/admin/threads/edit-document -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/admin/folders/([a-zA-Z0-9:/]{11,12}) -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/admin/folders/([a-zA-Z0-9:/]{11,12}) -H "Authorization: Bearer $at" | python -m json.tool
# curl http://platform.docker.qa:10000/1/admin/blob/([A-Za-z0-9]{11})/([A-Za-z0-9\-\_]{22})
curl 'http://platform.docker.qa:10000/1/admin/blob/JcUAAAls35b/IranRc-Ao96onSHA9ViNqQ?name=IDcard.pdf&company_id=FTGAcAzRzdg' -H "Authorization: Bearer $at" > filename.txt
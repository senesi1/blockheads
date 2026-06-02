# CONOP
## File repo
*Ray said he does not want this!*
User requests a file. We give it to them.

## Provenance tracker
*Ray said he wants this!*
User gets a file from a share folder or onedrive. They inform blockhead that they got it.

## Normal use
The User browses files through normal OS means. Shared folders. Outlook. Whatever.

When the user wants to read a file, he opens Blockhead and drags the file to it.

Blockhead hashes the file, POSTS to /checkout, and adds a row to a local sqlite3 database: filename, filehash

The user uses any app he likes to view and/or modify the file.

When he's done, he drags the file to Blockhead again.

Blockhead hashes the file, looks up the old hash in the sqlite3 database using the filename, POSTS to /checkin, and finally deletes the file from the sqlite3 database.

## Enclave transfer (if distinct servers)
The admin logs in as `username=enclave_brave` to Enclave Alpha and checks out the file, as above

The admin logs in as `username=enclave_alpha` to Enclave Bravo and checks in the file with `oldhash=null`

## Example
```
Bob checks out README.md with hash 3141
Charlie checks it out, too.
Bob modifies it and checks in hash 3141 -> 2718
Charlie modifies it and checks in hash 3141 -> 1618

Now Blockhead knows:

         -----2718 ---- ba05(ts)
        /
    3141------1618 ---- fa91(ts)
        \
         -----dead ---- 9275(ts)
                   \
                    --- a384(u)
```

## What gets hashed?
* File contents
* Permissions?
* Security level

# API
## /checkout
### Request
```http
POST /checkout
```

### Body
```json
{
  "username": "alice",
  "clearance": "secret",
  "filehash": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
```

### Response
```http
200 OK
404 Not Found (Doesn't exist or you don't have access)
```

## /checkin
### Request
```http
POST /checkin
```

### Body
```json
{
  "username": "alice",
  "clearance": "secret",
  "oldhash": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
  "newhash": "486ea46224d1bb4fb680f34f7c9ad96a8f24ec88be73ea8e5a6c65260e9cb8a7"
}
```

### Response
```http
200 OK
404 Not Found
```

# Architecture
## Common server
![diagram](png/common-server.png)

## Distinct enclaves
![diagram](png/distinct-enclaves.png)

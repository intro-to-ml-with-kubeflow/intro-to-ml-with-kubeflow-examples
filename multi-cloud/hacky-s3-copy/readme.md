

## Update py file w you s3 creds

From Credential JSON -> Python

`apikey` : `COS_API_KEY_ID`
`resource_instance_id` : `COS_RESOURCE_CRN`

Also make sure COS_ENDPOINT and COS_BUCKET_LOCATION line up (e.g. us-east and `http://s3.us-east...`)

## update yaml file w your project name

```bash
echo $GOOGLE_PROJECT
```

Then
```
pico *yaml
```

and replace $GOOG_PROJECT w your project

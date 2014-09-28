#!/bin/bash
NOW=$(date +"%F")
FILENAME="$NOW-longboxed-backup.sql"

echo '-----> Syncing production and staging S3 buckets....'
aws s3 sync s3://longboxed_dokku s3://lbstaging
echo '-----> Backing up production S3 bucket to backup S3 bucket....'
aws s3 sync s3://longboxed_dokku/ s3://longboxedbackup/longboxed_s3
echo '-----> Dumping production database...'
dokku postgresql:dump longboxed > /root/backup/longboxed_database/$FILENAME
echo '-----> Backing up database dumps...'
aws s3 sync /root/backup/longboxed_database/ s3://longboxedbackup/longboxed_database
echo '-----> Syncing production database dump to staging machine...'
rsync -a /root/backup/longboxed_database/$FILENAME root@staging.longboxed.com:/root/backup/longboxed_database/$FILENAME
echo '-----> Restoring exported database on staging server...'
ssh -T root@staging.longboxed.com FILENAME=$FILENAME <<'ENDSSH' > /dev/null
	"dokku postgresql:restore staging < /root/backup/longboxed_database/$FILENAME"
ENDSSH
echo 'Longboxed Database Sync Complete!'

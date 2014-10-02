#/bin/bash
export PATH="/root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games"

NOW=$(date +"%F")
FILENAME="$NOW-longboxed-backup.sql"

echo "-----: $NOW - Longboxed Sync :-----"
echo '-----> Syncing production and staging S3 buckets....'
aws s3 sync s3://longboxed s3://lbstaging
echo '-----> Backing up production S3 bucket to backup S3 bucket....'
aws s3 sync s3://longboxed/ s3://longboxedbackup/longboxed_s3
echo '-----> Dumping production database...'
dokku postgresql:dump longboxed > /root/backup/longboxed_database/$FILENAME
echo '-----> Backing up database dumps...'
aws s3 sync /root/backup/longboxed_database/ s3://longboxedbackup/longboxed_database
echo '-----> Syncing production database dump to staging machine...'
rsync -a /root/backup/longboxed_database/$FILENAME root@dev.longboxed.com:/root/backup/longboxed_database/$FILENAME
echo '-----> Restoring exported database on staging server...'
#ssh root@staging.longboxed.com FILENAME=$FILENAME <<'ENDSSH'
#	"dokku postgresql:restore staging < /root/backup/longboxed_database/$FILENAME"
#ENDSSH
echo "-----: $NOW - Longboxed Sync :-----" >> /home/logs/db_restore_log.txt
ssh root@dev.longboxed.com \
    "dokku postgresql:restore staging < /root/backup/longboxed_database/$FILENAME" \
    >> /home/logs/db_restore_log.txt 2>&1\
    /
echo 'Longboxed Database Sync Complete!'

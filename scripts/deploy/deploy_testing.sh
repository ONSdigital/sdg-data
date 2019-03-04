#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

echo "TRAVIS_BRANCH = " $TRAVIS_BRANCH
echo "TRAVIS_PULL_REQUEST_BRANCH = " $TRAVIS_PULL_REQUEST_BRANCH
echo "TRAVIS_TAG = " $TRAVIS_TAG

if [ "$TRAVIS_PULL_REQUEST" != "false" -o "$TRAVIS_BRANCH" = "master" ]; then
    echo "Skipping deploy; just doing a build."
    exit 0
fi

# Pull requests and commits to other branches shouldn't try to deploy, just build to verify
BASEURL=$TRAVIS_BRANCH
# slugify
BASEURL=$(echo "$BASEURL" | iconv -t ascii//TRANSLIT | sed -r s/[^a-zA-Z0-9]+/-/g | sed -r s/^-+\|-+$//g | tr A-Z a-z)

# Keys
openssl aes-256-cbc -K $encrypted_110f8461dee3_key -iv $encrypted_110f8461dee3_iv -in scripts/deploy/keys.tar.enc -out scripts/deploy/keys.tar -d
tar xvf scripts/deploy/keys.tar -C scripts/deploy/
rm scripts/deploy/keys.tar

chmod 600 ./scripts/deploy/deploy_key_test
eval `ssh-agent -s`
ssh-add scripts/deploy/deploy_key_test

# Push the files over, removing anything existing already.
ssh -oStrictHostKeyChecking=no travis@$TEST_SERVER "rm -rf ~/www/data/$BASEURL || true"
rsync -rvzh -e "ssh -i scripts/deploy/deploy_key_test -oStrictHostKeyChecking=no" --checksum --link-dest="../develop" _site/ travis@$TEST_SERVER:~/www/data/$BASEURL
rm scripts/deploy/deploy_key*

# next-version: lint test-configs test
# 		$(eval NEXT_VERSION := $(shell bumpversion --dry-run --allow-dirty --list $(VERSION_PART) | grep new_version | sed s,"^.*=",,))
# 		@echo Next version is $(NEXT_VERSION)
# 		bumpversion $(VERSION_PART)
# 		@echo "Review your version changes first"
# 		@echo "Accept your version: \`make accept-version\`"
# 		@echo "Revoke your version: \`make revoke-version\`"
#
# accept-version:
# 		git push && git push --tags
#
# revoke-version:
# 		git tag -d `git describe --tags --abbrev=0`    # delete the tag
# 		git reset --hard HEAD~1                        # rollback the commit
#
# dist:
# 		poetry build
#
# release-test: dist
# 		poetry publish --repository testpypi
#
# release: dist
# 		poetry publish
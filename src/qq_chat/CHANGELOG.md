# Changelog

## [2.3.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/qq_chat-v2.2.0...qq_chat-v2.3.0) (2024-09-25)


### Features

* **qq_chat:** :sparkles: 'force_bound' config && unbound msg from sync group could be forward to mc ([0506aba](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/0506aba3114c7ec1071e845d21f1f3c7155ddb01))


### Bug Fixes

* **qq_chat:** :fire: remove 'force_bound' config ([1d4b2ac](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/1d4b2ac8a05f57a7357559395fe8847d784d16fa))

## [2.2.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/qq_chat-v2.1.0...qq_chat-v2.2.0) (2024-08-01)


### Features

* **qq_chat:** :sparkles: support '@' instead qq number && whitelist add command template ([9d8e755](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/9d8e75586972403d2a37e652e7533ff3bb3d5e49))

## [2.1.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/qq_chat-v2.0.0...qq_chat-v2.1.0) (2023-06-29)


### Features

* **qq_chat:** :sparkles: multi server support ([#131](https://github.com/AnzhiZhang/MCDReforgedPlugins/issues/131)) ([a573d0b](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/a573d0b6e83edf55375d2fb7c553a8f830d5eeea))


### Bug Fixes

* **qq_chat:** :bug: fix all message which starts with long command prefix returns help msg ([5787d03](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/5787d038c5edd490da16016aeaf4edc0eb4e4d6f))
* **qq_chat:** :bug: remove forwards config. move forward feature to sync group ([6126ab9](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/6126ab9bd7c266576ed02e99f8262b32bf6a9754))

## [2.0.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/qq_chat-v1.0.1...qq_chat-v2.0.0) (2023-05-21)


### ⚠ BREAKING CHANGES

* **qq_chat:** remove  `groups` in `config.json`, please fill in the id in the original `groups` into `message_sync_groups` to maintain the original performance

### Features

* **qq_chat:** ✨ add player_list_regex config ([67649b6](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/67649b6e5038c481e65b1bfbb62e9d1e41f458d8))
* **qq_chat:** ✨ remove bot category in list command ([58e8dcd](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/58e8dcd46424fe6fd710ae1f3cbc74644078cfc5))
* **qq_chat:** 💥 2.0.0 ([6647439](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/66474399f6b0ccc086fb3c1072d72a8e2bf2862b))


### Bug Fixes

* **qq_chat:** 🐛 fix 'mc' command in main group invalid ([2d0c191](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/2d0c1910940a1f995189bdf810539fcc92fbf8fd))
* **qq_chat:** 🐛 use reply instead of bot.sync.send_group_msg ([b28d4b5](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/b28d4b57f8bd60db1b41880def7afee1706903e6))

## [1.0.1](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/qq_chat-v1.0.0...qq_chat-v1.0.1) (2023-02-26)


### Bug Fixes

* **qq_api:** 🐛 use event loop from qq_api ([c9ba896](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/c9ba8966bb2bc9105b3c0fe8b7802b5378e50509))

## 1.0.0 (2023-02-03)


### Features

* **qq_chat:** ✨ compatible with MCDR 2.0 ([32bcc63](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/32bcc63a6581742688d80b496d23de065f1d4586))
* **qq_chat:** ✨ compatible with MCDR 2.0 ([d60e2a9](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/d60e2a9faa0d8b4a0d685d99c8164bf6d4535ff9))

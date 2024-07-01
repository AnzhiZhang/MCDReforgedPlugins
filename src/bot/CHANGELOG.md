# Changelog

## [1.1.5](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.1.4...bot-v1.1.5) (2024-07-01)


### Bug Fixes

* **bot:** 🐛 save bot actual mc name (fix [#193](https://github.com/AnzhiZhang/MCDReforgedPlugins/issues/193)) ([56b7826](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/56b78266adacd52ac567c078dcbb42ff99ee549e))

## [1.1.4](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.1.3...bot-v1.1.4) (2024-03-15)


### Bug Fixes

* **bot:** 🐛 fix bot join detection bug ([1a367ce](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/1a367cecd27c9a623f91a0641167b5e4faa16af3))

## [1.1.3](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.1.2...bot-v1.1.3) (2024-02-27)


### Bug Fixes

* **bot:** 🐛 fix bot gamemode issue (fix [#186](https://github.com/AnzhiZhang/MCDReforgedPlugins/issues/186)) ([250b0da](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/250b0dae2a26b18f9e4c1183d442d5e2c2535787))
* **bot:** 🐛 fix bot naming issue ([5e9d240](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/5e9d24098a95b0b4aa34c2920da24373863e5c9a))


### Performance Improvements

* **bot:** ⚡️ improve perf of get_location ([a3ebfeb](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/a3ebfebe2cdb1c4a09a81870cb80f5be0a271e71))

## [1.1.2](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.1.1...bot-v1.1.2) (2024-01-15)


### Bug Fixes

* **bot:** 🐛 fix fastapi lib loading issue (fix [#161](https://github.com/AnzhiZhang/MCDReforgedPlugins/issues/161)) ([27738a6](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/27738a68833051de821928febac110252b532e63))

## [1.1.1](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.1.0...bot-v1.1.1) (2023-12-31)


### Bug Fixes

* **bot:** 🐛 fix fastapi import bug ([b0eccdb](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/b0eccdb2e66f3215d10df40a4237d18187183c4e))
* **bot:** 🔇 update logging level in FastAPIManager ([4cbe835](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/4cbe83526aff21533b181f3f30459b7f9f331584))

## [1.1.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.0.6...bot-v1.1.0) (2023-12-21)


### Features

* **bot:** ✨ always parse name in command handlers ([cfdf9ba](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/cfdf9bafee63bdab12be5d934d158b36f1e1ab7d))
* **bot:** ✨ config check ([cc5b2ae](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/cc5b2ae2263caa00165e000dcb4d751b78628636))
* **bot:** ✨ fastapi_mcdr support (resolve [#145](https://github.com/AnzhiZhang/MCDReforgedPlugins/issues/145)) ([b75aa6e](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/b75aa6e040e3db750fdc2a77f2588c0440e0d71e))
* **bot:** ✨ set bot online in post and patch requests ([4c41ab8](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/4c41ab86f2b9ca34f979c9620286b2ca016e2451))
* **bot:** ✨ set default name_prefix config to `bot_` ([15338b3](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/15338b3660c2e204e1d6e7944a97facd6210084d))
* **bot:** ✨ tags and auto update ([e67ba25](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/e67ba2549020b8d0649d2b6450c5756c1572b585))
* **bot:** 🌐 update english help message ([8c58216](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/8c5821663e707fd097bf7c2a0ed18f93c6c16b0a))


### Bug Fixes

* **bot:** 🐛 fix name in fastapi_manager and improve code style ([bce91f0](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/bce91f08e96b11bd58cbdcbd06fea998f2fa9efa))

## [1.0.6](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.0.5...bot-v1.0.6) (2023-01-19)


### Bug Fixes

* **bot:** 🐛 fix bot name uppercase issue ([0ea1824](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/0ea1824469e28244398fd9eb115793e4ec7be32f))

## [1.0.5](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.0.4...bot-v1.0.5) (2022-12-29)


### Build System

* **bot:** ⬆️ set mcdreforged denpendcy as ^2.6.0 ([2fbcabf](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/2fbcabf5ad021270b415af9a6c79b4598c725c3f))

## [1.0.4](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.0.3...bot-v1.0.4) (2022-12-29)


### Reverts

* **bot:** 💡 sort Union type order same as import order ([a5aca65](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/a5aca65f7ae4abb19aed5a4958d7f61857334d90))


### Build System

* **bot:** 🔖 1.0.4 ([ee00c3b](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/ee00c3b0f3e4588eb47fcdb51a275094fc14cf7a))

## [1.0.3](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.0.2...bot-v1.0.3) (2022-07-23)


### Bug Fixes

* **bot:** ✏️ fix help message arguments typo ([f4337ed](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f4337ed63f2ee5f8dcc5323d7d0bc9b6becdeed3))
* **bot:** 🐛 correcting usages of IllegalDimensionException ([a89d530](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/a89d5309041bdc25c3eddbe495f6069b785f8eaf))

## [1.0.2](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.0.1...bot-v1.0.2) (2022-07-22)


### Bug Fixes

* **bot:** 🐛 pass arg for raise exception ([22c74d6](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/22c74d6d08a49445e3f0cb8e9f4b7ebcd6ecda94))

## [1.0.1](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v1.0.0...bot-v1.0.1) (2022-07-21)


### Bug Fixes

* **bot:** ✨ add config button for actions in info ([16fd490](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/16fd490b75374ce3b0e43c6a792bf5a5ff0d48d5))

## [1.0.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/bot-v0.1.0...bot-v1.0.0) (2022-07-21)


### ⚠ BREAKING CHANGES

* **bot:** new dependencies

### Features

* **bot:** ✨ support incomplete location info in  save command ([130afc5](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/130afc5d441136a695a160d2c6e5907cd3a5a4a0))
* **bot:** 💥 rewrite to the new generation! ([bf5d450](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/bf5d450e0e507a3e4e232f5b1161bf5460ea271d))


### Bug Fixes

* **bot:** 🐛 disable data file load echo in console ([8065d64](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/8065d64c03d4c6c34ab963218ea0ad93f7578353))
* **bot:** 🐛 fix config button hover text color ([aac82c9](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/aac82c9c7aeb8a5ad2b98cfca9aec08d393c7661))
* **bot:** 🐛 fix config command using wrong permission to check ([3ddb723](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/3ddb723299f3acb4038fbe00288c7c4c34afde6b))
* **bot:** 🐛 fix gamemode setting on spawn bot ([40e8678](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/40e86788c66110aa40b61ecf244d913c791c043e))
* **bot:** 🐛 fix help message error ([2300400](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/2300400f193ebf4b7073985ea19b7edbefe32a63))

## 0.1.0 (2022-06-30)


### Features

* **bot:** ✨ support MCDR 2.0 ([a8db9a7](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/a8db9a7dabd23011ab9eed81c0ca1429369581ec))

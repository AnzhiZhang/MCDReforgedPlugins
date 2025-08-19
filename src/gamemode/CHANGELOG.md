# Changelog

## [1.4.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/gamemode-v1.3.0...gamemode-v1.4.0) (2025-08-19)


### Features

* **gamemode:** allow teleport to players ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** features and bux fixes ([#282](https://github.com/AnzhiZhang/MCDReforgedPlugins/issues/282)) ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** rotate player to initial angle when switching from spectator to survival mode ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** support configurable data.json save path ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** support configurable short_commands ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** support tilde(`~`) in `tp` command ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** update config file ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** update help message ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** validate player param online using online_player_api ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))


### Bug Fixes

* **gamemode:** fix `!!spec <player>` exception when player doesn't exist ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** improve coordinate validation using regex ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** initialize loop_manager to None ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))
* **gamemode:** normalize player name when using another player's name ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))


### Performance Improvements

* **gamemode:** remove duplicate player position queries; Optimize player position queries ([f289890](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/f2898902adc430256973450843da42ee2be5bebd))

## [1.3.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/gamemode-v1.2.0...gamemode-v1.3.0) (2025-08-17)


### Features

* ✨ update config ([6a66116](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/6a6611663f53edceec740dd85f63ef142c8a91d9))

## [1.2.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/gamemode-v1.1.0...gamemode-v1.2.0) (2025-08-17)


### Features

* **gamemode:** range limit ([304a078](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/304a078a3addd0213bd1804bdb819f4beef25eab))
* **gamemode:** update command requirements ([b0a7b91](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/b0a7b91fb51bbe6982ac3a02d23deaffa86d753d))


### Bug Fixes

* **gamemode:** load monitored players on load ([5b73651](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/5b7365145433a2b7c7f89aac52c204059c96b56e))

## [1.1.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/gamemode-v1.0.1...gamemode-v1.1.0) (2023-12-26)


### Features

* **gamemode:** ✨ add shorter command !s ([5ac0725](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/5ac0725dc950478e5d21d275eb8d6a2c6dbc0e81))
* **gamemode:** ✨ update help messsage ([015850e](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/015850ea4c8c9faa54872b7e927ef9ac707b9625))

## [1.0.1](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/gamemode-v1.0.0...gamemode-v1.0.1) (2023-03-18)


### Bug Fixes

* **gamemode:** 👽️ fix config api issue (fix [#114](https://github.com/AnzhiZhang/MCDReforgedPlugins/issues/114)) ([2ed962f](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/2ed962f914adfc9184e228bf7b80161482136968))

## [1.0.0](https://github.com/AnzhiZhang/MCDReforgedPlugins/compare/gamemode-v0.1.0...gamemode-v1.0.0) (2022-12-02)


### Bug Fixes

* **gamemode:** 🐛 fix load_config_simple as MCDR api changed (fix [#68](https://github.com/AnzhiZhang/MCDReforgedPlugins/issues/68)) ([2dd500e](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/2dd500edf5978cff513e2aa5c638276f7e2963cb))


### Miscellaneous Chores

* **gamemode:** 🔖 1.0.0 ([1369ad8](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/1369ad83260f3b5a99ab1a5ada387f5f7042e755))

## 0.1.0 (2022-06-30)


### Features

* **gamemode:** ✨ support MCDR 2.0 ([d999f4a](https://github.com/AnzhiZhang/MCDReforgedPlugins/commit/d999f4aa3ea606dd26c98643f18ed5cf47d64664))

# Changelog

## [1.50.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.50.0...v1.50.1) (2026-11-03)


### Bug Fixes

* **agents:** call the Vikunja entity tool with its subcommand argument ([6ecb99f](https://github.com/dryvist/ai-llm-prompts/commit/6ecb99fe1e4791716989cc979093762f978adf9d))
* **agents:** use the vikunja_tasks entity tool with subcommand ([#223](https://github.com/dryvist/ai-llm-prompts/issues/223)) ([6ecb99f](https://github.com/dryvist/ai-llm-prompts/commit/6ecb99fe1e4791716989cc979093762f978adf9d))

## [1.50.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.49.1...v1.50.0) (2026-11-03)


### Features

* **agents:** add docs-updater and compose the vikunja-clerk classifier from the shared prefix ([#218](https://github.com/dryvist/ai-llm-prompts/issues/218)) ([a9a42de](https://github.com/dryvist/ai-llm-prompts/commit/a9a42debbcaf8056d70d9bca7adaa806d18e9df3))

## [1.49.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.49.0...v1.49.1) (2026-11-02)


### Bug Fixes

* **agents:** generate Dify DSL fields from agent YAML and give vikunja-triage its own scope ([#216](https://github.com/dryvist/ai-llm-prompts/issues/216)) ([6ccdd18](https://github.com/dryvist/ai-llm-prompts/commit/6ccdd18501a44623b130cd7d3926958851e3746a))

## [1.49.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.48.0...v1.49.0) (2026-11-02)


### Features

* **agents:** render Dify DSLs from templates, the shared prefix and each agent prompt ([#214](https://github.com/dryvist/ai-llm-prompts/issues/214)) ([fd50ecb](https://github.com/dryvist/ai-llm-prompts/commit/fd50ecb83f88090fc5590a562a51b4a5268c1e4d))

## [1.48.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.47.1...v1.48.0) (2026-11-02)


### Features

* **agents:** add the shared homelab prefix and an agent definition contract test ([#211](https://github.com/dryvist/ai-llm-prompts/issues/211)) ([61b5a96](https://github.com/dryvist/ai-llm-prompts/commit/61b5a96e99ed6354adbccc76838e1c33677b34f6))

## [1.47.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.47.0...v1.47.1) (2026-11-02)


### Bug Fixes

* **rules:** state the 10-minute component rule in the operator's terms ([#209](https://github.com/dryvist/ai-llm-prompts/issues/209)) ([6c345f7](https://github.com/dryvist/ai-llm-prompts/commit/6c345f730a15fcda4c33d5506821c5806702fec6))

## [1.47.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.46.0...v1.47.0) (2026-11-02)


### Features

* **rules:** every component runs in under 10 minutes ([#207](https://github.com/dryvist/ai-llm-prompts/issues/207)) ([b87ac7a](https://github.com/dryvist/ai-llm-prompts/commit/b87ac7aa79a7de254533d22c7bfbe8bfb5b8c7db))

## [1.46.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.45.0...v1.46.0) (2026-11-02)


### Features

* **agents:** add a scheduled zammad-triage Workflow in shadow ([#205](https://github.com/dryvist/ai-llm-prompts/issues/205)) ([dde8639](https://github.com/dryvist/ai-llm-prompts/commit/dde8639c64058e2fcf44729c0e36f7988f3a21c1))

## [1.45.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.44.0...v1.45.0) (2026-11-02)


### Features

* **evals:** set the expected-output scoring mode per suite, strict for the vikunja clerk ([#203](https://github.com/dryvist/ai-llm-prompts/issues/203)) ([ef693a0](https://github.com/dryvist/ai-llm-prompts/commit/ef693a067a48bb7025bd04bd6e7441f5747d9c00))

## [1.44.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.43.0...v1.44.0) (2026-11-02)


### Features

* **evals:** score expected output by field, patches by behavior, and the rubric with two judges ([#201](https://github.com/dryvist/ai-llm-prompts/issues/201)) ([e8d4914](https://github.com/dryvist/ai-llm-prompts/commit/e8d49143ae0c91b527c92e7712405ca8151d7ad0))

## [1.43.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.42.0...v1.43.0) (2026-11-02)


### Features

* **evals:** add the promptfoo agent evaluation matrix harness ([#199](https://github.com/dryvist/ai-llm-prompts/issues/199)) ([4523af2](https://github.com/dryvist/ai-llm-prompts/commit/4523af205cb23cf0a674d57102365ceb3721a2b8))

## [1.42.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.41.0...v1.42.0) (2026-11-02)


### Features

* **evals:** match clerk refusal reasons against keyword lists ([#197](https://github.com/dryvist/ai-llm-prompts/issues/197)) ([26891e6](https://github.com/dryvist/ai-llm-prompts/commit/26891e60326a97a96779895daa592d64586a447f))

## [1.41.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.40.0...v1.41.0) (2026-11-02)


### Features

* **evals:** add contract-derived parse expectations to the vikunja-clerk eval ([#195](https://github.com/dryvist/ai-llm-prompts/issues/195)) ([e3954a9](https://github.com/dryvist/ai-llm-prompts/commit/e3954a96bd386859e9594f2a50afa0d819df1e5e))

## [1.40.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.39.0...v1.40.0) (2026-11-02)


### Features

* **agents:** add a scheduled vikunja-triage Workflow in shadow ([#193](https://github.com/dryvist/ai-llm-prompts/issues/193)) ([6b7419f](https://github.com/dryvist/ai-llm-prompts/commit/6b7419f4d3c7cb2c7bec43b78ab00adea63b5900))

## [1.39.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.38.0...v1.39.0) (2026-11-02)


### Features

* **agents:** add Vikunja parse judge evaluators as code ([#191](https://github.com/dryvist/ai-llm-prompts/issues/191)) ([81b699c](https://github.com/dryvist/ai-llm-prompts/commit/81b699c280fa1f5c78940d43c98922e772c76e29))

## [1.38.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.37.2...v1.38.0) (2026-11-02)


### Features

* **evals:** add capability scenarios for basic agent operations ([#189](https://github.com/dryvist/ai-llm-prompts/issues/189)) ([bf66b54](https://github.com/dryvist/ai-llm-prompts/commit/bf66b541d208a7a784c88eb80014b8b629a663df))

## [1.37.2](https://github.com/dryvist/ai-llm-prompts/compare/v1.37.1...v1.37.2) (2026-11-01)


### Bug Fixes

* **agents:** take vikunja-clerk scope from the Mandate and refuse incidents by default ([#187](https://github.com/dryvist/ai-llm-prompts/issues/187)) ([13c710e](https://github.com/dryvist/ai-llm-prompts/commit/13c710e5104d9be9cc7497dc336c5e4d6da28bf7))

## [1.37.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.37.0...v1.37.1) (2026-11-01)


### Bug Fixes

* **agents:** tighten fleet agent guards, triggers and eval fixtures ([#185](https://github.com/dryvist/ai-llm-prompts/issues/185)) ([05b8fed](https://github.com/dryvist/ai-llm-prompts/commit/05b8fed0149582273a8d1063c0131b1506c2eccb))

## [1.37.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.36.0...v1.37.0) (2026-11-01)


### Features

* **agents:** let vikunja-clerk file and update tasks in guarded projects ([#183](https://github.com/dryvist/ai-llm-prompts/issues/183)) ([b76e7bf](https://github.com/dryvist/ai-llm-prompts/commit/b76e7bf8294fd09289b29e1fbf6961cd7f96a80f))

## [1.36.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.35.0...v1.36.0) (2026-11-01)


### Features

* **agents:** run fleet agents in shadow mode bound to a mandate ([#181](https://github.com/dryvist/ai-llm-prompts/issues/181)) ([e34b783](https://github.com/dryvist/ai-llm-prompts/commit/e34b783d7fbcfd7565f2243bf064ca8740bad405))

## [1.35.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.34.0...v1.35.0) (2026-11-01)


### Features

* **agents:** add the vikunja-clerk agent definition ([#179](https://github.com/dryvist/ai-llm-prompts/issues/179)) ([1463a11](https://github.com/dryvist/ai-llm-prompts/commit/1463a11deb1b856b81914b5877129be980e579a3))

## [1.34.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.33.0...v1.34.0) (2026-11-01)


### Features

* **agents:** add the ci-fixer and code-simplifier agent definitions ([#177](https://github.com/dryvist/ai-llm-prompts/issues/177)) ([b5956b9](https://github.com/dryvist/ai-llm-prompts/commit/b5956b9c45f836f7a2b579f4feddc34b751268b4))

## [1.33.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.32.0...v1.33.0) (2026-11-01)


### Features

* **rules:** define the scope of central documentation ([#175](https://github.com/dryvist/ai-llm-prompts/issues/175)) ([4137f0d](https://github.com/dryvist/ai-llm-prompts/commit/4137f0db679a3292b888914be0a4f659abce600d))

## [1.32.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.31.0...v1.32.0) (2026-11-01)


### Features

* **prompts:** add a staged Slack interactor contract ([e3d8e7c](https://github.com/dryvist/ai-llm-prompts/commit/e3d8e7c3caf3632f6e150f84cfaa78a322e28e36))
* **prompts:** add a staged Slack interactor contract ([#171](https://github.com/dryvist/ai-llm-prompts/issues/171)) ([488366e](https://github.com/dryvist/ai-llm-prompts/commit/488366e09db4ba3def760b4dab56fb6190db815a))


### Bug Fixes

* allow authorized first Slack sends without correlation state ([73491b5](https://github.com/dryvist/ai-llm-prompts/commit/73491b5d852616f6a352ac4d8e1dcff9a1559fc7))
* **prompts:** keep the Slack interactor contract concise ([3be4ce2](https://github.com/dryvist/ai-llm-prompts/commit/3be4ce2c0afe2d8d060aa16738937747e918694b))

## [1.31.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.30.0...v1.31.0) (2026-11-01)


### Features

* **prompts:** add a staged Vikunja specialist contract ([#170](https://github.com/dryvist/ai-llm-prompts/issues/170)) ([b60d35e](https://github.com/dryvist/ai-llm-prompts/commit/b60d35e59d8ef5d9bc20fa753ec4d2bad53fdd95))

## [1.30.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.29.2...v1.30.0) (2026-11-01)


### Features

* **prompts:** add a draft GitHub specialist contract ([b59709e](https://github.com/dryvist/ai-llm-prompts/commit/b59709e4f59359a38857f996a503023967daff2d))
* **prompts:** add a draft GitHub specialist contract ([#169](https://github.com/dryvist/ai-llm-prompts/issues/169)) ([ebfe323](https://github.com/dryvist/ai-llm-prompts/commit/ebfe323c1383e11bf66d7ba8f3f8327851f63f81))

## [1.29.2](https://github.com/dryvist/ai-llm-prompts/compare/v1.29.1...v1.29.2) (2026-10-31)


### Bug Fixes

* **instructions:** state one delegation routing order in AGENTS.md ([#167](https://github.com/dryvist/ai-llm-prompts/issues/167)) ([7cd3f95](https://github.com/dryvist/ai-llm-prompts/commit/7cd3f950da361381be233ffd09b3584e88c57fa0))

## [1.29.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.29.0...v1.29.1) (2026-10-30)


### Bug Fixes

* **prompts:** use configured memory for monitoring ([c82d004](https://github.com/dryvist/ai-llm-prompts/commit/c82d0042024f5e07e019e0e4e9a44a3e2d7ce704))

## [1.29.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.28.0...v1.29.0) (2026-10-30)


### Features

* use configured Herdr for agent orchestration ([#163](https://github.com/dryvist/ai-llm-prompts/issues/163)) ([0a90b84](https://github.com/dryvist/ai-llm-prompts/commit/0a90b846b9495f48df483b8a0e747d40f60a194c))

## [1.28.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.27.1...v1.28.0) (2026-10-29)


### Features

* **git-flow:** document Main Source Gate allow-list ([#161](https://github.com/dryvist/ai-llm-prompts/issues/161)) ([b25f737](https://github.com/dryvist/ai-llm-prompts/commit/b25f737b9ed2ac764c0ac45b143a1e7eb5f4aa96))

## [1.27.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.27.0...v1.27.1) (2026-10-29)


### Bug Fixes

* **rules:** native schedule skew satisfies the schedule rule ([#159](https://github.com/dryvist/ai-llm-prompts/issues/159)) ([0e4ed84](https://github.com/dryvist/ai-llm-prompts/commit/0e4ed842d203e8a4f5e2c4af4acf4b3147a461c1))

## [1.27.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.26.1...v1.27.0) (2026-10-29)


### Features

* **operating-core:** schedule off the round clock ([#157](https://github.com/dryvist/ai-llm-prompts/issues/157)) ([c7688de](https://github.com/dryvist/ai-llm-prompts/commit/c7688ded37294bd850323d4d73bd2f79febb2a68))

## [1.26.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.26.0...v1.26.1) (2026-10-28)


### Bug Fixes

* **delegation:** state what a Codex worker cannot do in its sandbox ([#155](https://github.com/dryvist/ai-llm-prompts/issues/155)) ([e83989d](https://github.com/dryvist/ai-llm-prompts/commit/e83989da63ac9e169863864e38d56eb1fe6d031d))

## [1.26.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.25.4...v1.26.0) (2026-10-28)


### Features

* **delegation:** document widening a blocked Codex worker ([#153](https://github.com/dryvist/ai-llm-prompts/issues/153)) ([4eb2d2c](https://github.com/dryvist/ai-llm-prompts/commit/4eb2d2cf29a8e21366fa0d3a99da381e69536995))

## [1.25.4](https://github.com/dryvist/ai-llm-prompts/compare/v1.25.3...v1.25.4) (2026-10-28)


### Bug Fixes

* agents hold PRs with draft or human:review and never arm auto-merge ([#147](https://github.com/dryvist/ai-llm-prompts/issues/147)) ([d821ee9](https://github.com/dryvist/ai-llm-prompts/commit/d821ee9dec29970e2268c2b9947af806fc4f9b98))

## [1.25.3](https://github.com/dryvist/ai-llm-prompts/compare/v1.25.2...v1.25.3) (2026-10-27)


### Bug Fixes

* **instructions:** start branches with git town hack ([#150](https://github.com/dryvist/ai-llm-prompts/issues/150)) ([f02f634](https://github.com/dryvist/ai-llm-prompts/commit/f02f63485611932db234d28c07a4cbef9b476bcc))

## [1.25.2](https://github.com/dryvist/ai-llm-prompts/compare/v1.25.1...v1.25.2) (2026-10-25)


### Bug Fixes

* **instructions:** name branches by Conventional Commits type ([#148](https://github.com/dryvist/ai-llm-prompts/issues/148)) ([ed93f2a](https://github.com/dryvist/ai-llm-prompts/commit/ed93f2a8c6fcc5ac1f400ffcf15750e244b36d5b))

## [1.25.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.25.0...v1.25.1) (2026-10-24)


### Bug Fixes

* **instructions:** drop the retired git-flow-next skill override ([#145](https://github.com/dryvist/ai-llm-prompts/issues/145)) ([51096a8](https://github.com/dryvist/ai-llm-prompts/commit/51096a891a69756b5765725d9898c920a77136c9))

## [1.25.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.24.0...v1.25.0) (2026-10-24)


### Features

* **instructions:** start and sync branches with Git Town ([#143](https://github.com/dryvist/ai-llm-prompts/issues/143)) ([e0afb49](https://github.com/dryvist/ai-llm-prompts/commit/e0afb49f0a39be4f6864c6cb143f4c7bf37d51ca))

## [1.24.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.23.0...v1.24.0) (2026-10-24)


### Features

* **instructions:** make model-delegation the single home of the Codex call contract ([#141](https://github.com/dryvist/ai-llm-prompts/issues/141)) ([88e33ce](https://github.com/dryvist/ai-llm-prompts/commit/88e33ce43209e07992f1bae0edd55b8a82bdd00e))

## [1.23.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.22.0...v1.23.0) (2026-10-24)


### Features

* **instructions:** start program-scale work with a tracker pass ([#139](https://github.com/dryvist/ai-llm-prompts/issues/139)) ([c6dce98](https://github.com/dryvist/ai-llm-prompts/commit/c6dce988098f609c4683486fd45b5af022956741))

## [1.22.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.21.3...v1.22.0) (2026-10-24)


### Features

* point prose writing at the user voice file ([#137](https://github.com/dryvist/ai-llm-prompts/issues/137)) ([554c5d0](https://github.com/dryvist/ai-llm-prompts/commit/554c5d0d78b8157a2aa8705b514a19d89afb5628))

## [1.21.3](https://github.com/dryvist/ai-llm-prompts/compare/v1.21.2...v1.21.3) (2026-10-18)


### Bug Fixes

* **instructions:** trim claude-code.md so the delivered CLAUDE.md stays within its token budget ([#135](https://github.com/dryvist/ai-llm-prompts/issues/135)) ([a8eb947](https://github.com/dryvist/ai-llm-prompts/commit/a8eb9472e8899573e3cef4e88a4e4ab99de99398))

## [1.21.2](https://github.com/dryvist/ai-llm-prompts/compare/v1.21.1...v1.21.2) (2026-10-18)


### Bug Fixes

* **instructions:** trim the core AGENTS.md so the delivered file stays within its token budget ([#133](https://github.com/dryvist/ai-llm-prompts/issues/133)) ([1dc436c](https://github.com/dryvist/ai-llm-prompts/commit/1dc436ceacdd791a9853305f0bfdf1fc0602c245))

## [1.21.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.21.0...v1.21.1) (2026-10-18)


### Bug Fixes

* **instructions:** drop load-gate contradiction and repeated rules from on-demand text ([#131](https://github.com/dryvist/ai-llm-prompts/issues/131)) ([cb166a2](https://github.com/dryvist/ai-llm-prompts/commit/cb166a249cd5e3e6837609924e25ed24d81d0533))

## [1.21.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.20.0...v1.21.0) (2026-10-18)


### Features

* **instructions:** name roles instead of products in the shared rules ([#129](https://github.com/dryvist/ai-llm-prompts/issues/129)) ([f572f51](https://github.com/dryvist/ai-llm-prompts/commit/f572f5198d3fcc0363480380fa680bfa78ca4841))

## [1.20.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.19.0...v1.20.0) (2026-10-18)


### Features

* **instructions:** delegate count is uncapped; only machine load gates fan-out ([#127](https://github.com/dryvist/ai-llm-prompts/issues/127)) ([dff2987](https://github.com/dryvist/ai-llm-prompts/commit/dff298737bdb184216d413e27114c5f4507583f7))

## [1.19.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.18.0...v1.19.0) (2026-10-18)


### Features

* **instructions:** move the shared global agent instructions into the catalog ([#125](https://github.com/dryvist/ai-llm-prompts/issues/125)) ([f2274b6](https://github.com/dryvist/ai-llm-prompts/commit/f2274b6ebcf372b6a16c1ed37c0640f8ace09834))

## [1.18.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.17.0...v1.18.0) (2026-10-18)


### Features

* **agents:** replace the model-named executors with one model-neutral executor ([#123](https://github.com/dryvist/ai-llm-prompts/issues/123)) ([3eb9c8e](https://github.com/dryvist/ai-llm-prompts/commit/3eb9c8ed42ed0c4bfacccc6cc515e32b1b815fe1))

## [1.17.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.16.1...v1.17.0) (2026-10-17)


### Features

* **hermes:** report promotion drift instead of opening draft PRs ([#119](https://github.com/dryvist/ai-llm-prompts/issues/119)) ([55d7547](https://github.com/dryvist/ai-llm-prompts/commit/55d754756a9c80a7967601d0eb86013c48b153ad))

## [1.16.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.16.0...v1.16.1) (2026-10-14)


### Bug Fixes

* **developer-tools:** clarify heading-only mentions in the disclosure judge prompt ([#116](https://github.com/dryvist/ai-llm-prompts/issues/116)) ([3d257b3](https://github.com/dryvist/ai-llm-prompts/commit/3d257b3d6deae089c2dd2674873a376a8c489324))

## [1.16.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.15.1...v1.16.0) (2026-10-14)


### Features

* **developer-tools:** add public disclosure judge prompt ([#114](https://github.com/dryvist/ai-llm-prompts/issues/114)) ([b4dd0aa](https://github.com/dryvist/ai-llm-prompts/commit/b4dd0aa28810b7389f39d372bc8c4b46bf84778c))

## [1.15.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.15.0...v1.15.1) (2026-10-13)


### Bug Fixes

* **auto-ai-agent:** maintain release-PR exclusion in manual lane ([#111](https://github.com/dryvist/ai-llm-prompts/issues/111)) ([f008d14](https://github.com/dryvist/ai-llm-prompts/commit/f008d14047fe74c1f5afda080072237be9fbff56))

## [1.15.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.14.1...v1.15.0) (2026-10-13)


### Features

* **auto-ai-agent:** pr-shepherd, promotion drift and shepherd sweep prompts ([#108](https://github.com/dryvist/ai-llm-prompts/issues/108)) ([15c7f03](https://github.com/dryvist/ai-llm-prompts/commit/15c7f03ad5b91f0bb028c6dfb4518ab6d2402b05))

## [1.14.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.14.0...v1.14.1) (2026-10-12)


### Bug Fixes

* **auto-ai-agent:** frame base rules as defaults and drop a duplicated output line ([115e2d6](https://github.com/dryvist/ai-llm-prompts/commit/115e2d64510e9a906ff93a5927b3abd98dd9f90f))
* **auto-ai-agent:** name router capabilities instead of retired roles in the Hermes persona ([bc94fc7](https://github.com/dryvist/ai-llm-prompts/commit/bc94fc7dad256a8e7c122dae568dacdac010de06))

## [1.14.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.13.0...v1.14.0) (2026-10-11)


### Features

* **auto-ai-agent:** add a manual-repo risk lane to bot PR triage ([#104](https://github.com/dryvist/ai-llm-prompts/issues/104)) ([8b7b9f2](https://github.com/dryvist/ai-llm-prompts/commit/8b7b9f27798cf3d1359f528ea0bc696f99b03f16))

## [1.13.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.12.1...v1.13.0) (2026-10-11)


### Features

* **automation:** seed the CI workbook with recurring failure signatures ([#96](https://github.com/dryvist/ai-llm-prompts/issues/96)) ([2b7e560](https://github.com/dryvist/ai-llm-prompts/commit/2b7e5605da4bd474463ce8901e627001f10c7679))

## [1.12.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.12.0...v1.12.1) (2026-10-10)


### Bug Fixes

* **hermes-curriculum:** rename the anomalous verdict to anomalous-escalate ([#92](https://github.com/dryvist/ai-llm-prompts/issues/92)) ([ef9e6c6](https://github.com/dryvist/ai-llm-prompts/commit/ef9e6c666f9ac8373120285ffca797854bf4f324))

## [1.12.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.11.0...v1.12.0) (2026-10-10)


### Features

* **auto-ai-agent:** subagent roster and the brief-delegates rule ([#87](https://github.com/dryvist/ai-llm-prompts/issues/87)) ([c174fd1](https://github.com/dryvist/ai-llm-prompts/commit/c174fd1d23fdb46d02167c8578a160a956732a52))

## [1.11.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.10.1...v1.11.0) (2026-10-09)


### Features

* **auto-ai-agent:** open-ended Splunk platform health prompt ([5422f0d](https://github.com/dryvist/ai-llm-prompts/commit/5422f0d5fec789f81be08bb6fe00c101fda49de0))
* **auto-ai-agent:** open-ended Splunk platform health prompt ([55e8ed8](https://github.com/dryvist/ai-llm-prompts/commit/55e8ed8fb8827c99646f2ec6bb11d6529196f7b7))

## [1.10.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.10.0...v1.10.1) (2026-10-08)


### Bug Fixes

* **prompt:** align Hermes service pulse contract ([#81](https://github.com/dryvist/ai-llm-prompts/issues/81)) ([d1822f4](https://github.com/dryvist/ai-llm-prompts/commit/d1822f4ae4aa1e7eeaa10a4b61a7a0fe8f8d7ad3))

## [1.10.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.9.2...v1.10.0) (2026-10-05)


### Features

* **prompts:** compose monitoring context for direct API ([9c6c2cf](https://github.com/dryvist/ai-llm-prompts/commit/9c6c2cf96528440266815511a478d666f8c8c70a))
* **prompts:** compose monitoring context for direct API ([d29b8ca](https://github.com/dryvist/ai-llm-prompts/commit/d29b8ca0ea780e57215f082d28cb2912d372477e))

## [1.9.2](https://github.com/dryvist/ai-llm-prompts/compare/v1.9.1...v1.9.2) (2026-10-04)


### Bug Fixes

* **hermes:** keep same-channel healthy runs silent ([#77](https://github.com/dryvist/ai-llm-prompts/issues/77)) ([0c02301](https://github.com/dryvist/ai-llm-prompts/commit/0c0230195cbf95beaaf8e5ba100eba19890211c5))

## [1.9.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.9.0...v1.9.1) (2026-10-04)


### Bug Fixes

* silence release watch when no releases qualify ([#75](https://github.com/dryvist/ai-llm-prompts/issues/75)) ([f3f8b57](https://github.com/dryvist/ai-llm-prompts/commit/f3f8b576faffacd63ef95bda2e37d275582b21b8))

## [1.9.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.8.0...v1.9.0) (2026-10-04)


### Features

* **auto-ai-agent:** add daily release-watch prompt ([74e42e8](https://github.com/dryvist/ai-llm-prompts/commit/74e42e8c4874d4ab016a5a8b8a327bbdb73edf44))
* **auto-ai-agent:** add Hermes release watch ([3a31c27](https://github.com/dryvist/ai-llm-prompts/commit/3a31c27a596ca7b1c351952e6e76bfeda1ca849f))


### Bug Fixes

* **auto-ai-agent:** add missing prompt source history ([2bd5868](https://github.com/dryvist/ai-llm-prompts/commit/2bd58680f00f9313e50a03c115fcc80a5ec0f9c1))
* **catalog:** trim legacy docs-sync changelog entry ([b72c174](https://github.com/dryvist/ai-llm-prompts/commit/b72c174b51becbe6a50abf7c1c2f5ece36f3544c))

## [1.8.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.7.0...v1.8.0) (2026-09-28)


### Features

* **auto-ai-agent:** direct-cron reporting footers, report only and no worker narration ([#71](https://github.com/dryvist/ai-llm-prompts/issues/71)) ([966a941](https://github.com/dryvist/ai-llm-prompts/commit/966a941b45c2b6daff27488ee40603c4fcf6bf09))

## [1.7.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.6.0...v1.7.0) (2026-09-28)


### Features

* **auto-ai-agent:** license audit reads Splunk system messages and health report ([#69](https://github.com/dryvist/ai-llm-prompts/issues/69)) ([5578e3f](https://github.com/dryvist/ai-llm-prompts/commit/5578e3f254773d6dcaca673e8e3d868d30718c4b))

## [1.6.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.5.0...v1.6.0) (2026-09-28)


### Features

* **auto-ai-agent:** Hermes service pulse and Splunk license audit prompts ([#67](https://github.com/dryvist/ai-llm-prompts/issues/67)) ([4d48094](https://github.com/dryvist/ai-llm-prompts/commit/4d480940aca09077de7497da95284dac5b677bc3))

## [1.5.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.4.0...v1.5.0) (2026-09-25)


### Features

* **automation:** add testing agent instruction bodies ([#64](https://github.com/dryvist/ai-llm-prompts/issues/64)) ([29acd77](https://github.com/dryvist/ai-llm-prompts/commit/29acd77b0cc2e4469877d07bcbffcf5c24182bc2))

## [1.4.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.3.0...v1.4.0) (2026-09-24)


### Features

* **automation:** add docs-sync prompt for per-merge CI enforcement ([5ba5971](https://github.com/dryvist/ai-llm-prompts/commit/5ba59716e046eb6dc5101ce7505b7dd251460bec))
* **automation:** add docs-sync prompt for per-merge CI enforcement ([ad9697c](https://github.com/dryvist/ai-llm-prompts/commit/ad9697cb92c54e4a41eb778df251cd0b76152eca))

## [1.3.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.2.3...v1.3.0) (2026-09-12)


### Features

* **auto-ai-agent:** add a once-daily stale-open-PR report to bot-pr-triage ([#60](https://github.com/dryvist/ai-llm-prompts/issues/60)) ([4e370ab](https://github.com/dryvist/ai-llm-prompts/commit/4e370ab05c1296ba5f2c5a1f820f058e4e9bf404))

## [1.2.3](https://github.com/dryvist/ai-llm-prompts/compare/v1.2.2...v1.2.3) (2026-09-12)


### Bug Fixes

* **hermes:** stop hardcoding physical model ids, name router roles ([#57](https://github.com/dryvist/ai-llm-prompts/issues/57)) ([3b6bf87](https://github.com/dryvist/ai-llm-prompts/commit/3b6bf87f39cb22ee16e9493f8ef426f30a9a4f09))

## [1.2.2](https://github.com/dryvist/ai-llm-prompts/compare/v1.2.1...v1.2.2) (2026-09-05)


### Bug Fixes

* **agents:** restore the trailing newline on AGENTS.md ([#54](https://github.com/dryvist/ai-llm-prompts/issues/54)) ([c8c8ce6](https://github.com/dryvist/ai-llm-prompts/commit/c8c8ce67b32cd6673734449818e36554a868bcec))

## [1.2.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.2.0...v1.2.1) (2026-09-01)


### Bug Fixes

* **hermes-github-triage:** pin the query and stop an implausible total ([#51](https://github.com/dryvist/ai-llm-prompts/issues/51)) ([e435425](https://github.com/dryvist/ai-llm-prompts/commit/e435425700766b02ccaaedbe98bafb6accd01d60))

## [1.2.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.1.1...v1.2.0) (2026-08-20)


### Features

* **auto-ai-agent:** add disclosure routing law to autonomous base prompt ([fa6a06f](https://github.com/dryvist/ai-llm-prompts/commit/fa6a06f5230c971fe9fc1bbe66cfad648ba9b8bd))

## [1.1.1](https://github.com/dryvist/ai-llm-prompts/compare/v1.1.0...v1.1.1) (2026-08-15)


### Bug Fixes

* **automation:** split oversized log and repo-audit files under the size gate ([#47](https://github.com/dryvist/ai-llm-prompts/issues/47)) ([140cec3](https://github.com/dryvist/ai-llm-prompts/commit/140cec38a5f861a351c0e6727cccf649e6982757))

## [1.1.0](https://github.com/dryvist/ai-llm-prompts/compare/v1.0.0...v1.1.0) (2026-08-11)


### Features

* **hermes-docs-sync:** correct docs that restate a stale version ([032c804](https://github.com/dryvist/ai-llm-prompts/commit/032c8042c17f40a6893218a274b22446a022e68b))
* **hermes-docs-sync:** correct docs that restate a stale version ([#45](https://github.com/dryvist/ai-llm-prompts/issues/45)) ([401e9e4](https://github.com/dryvist/ai-llm-prompts/commit/401e9e42dcb1f3b6cbbf28854e93bc74b961da69))

## [1.0.0](https://github.com/dryvist/ai-llm-prompts/compare/v0.9.0...v1.0.0) (2026-08-06)


### ⚠ BREAKING CHANGES

* **prompts:** dryvist/claude-code-routines no longer renders any prompt from automation/. The retired resource IDs remain resolvable for history.

### Bug Fixes

* **prompts:** restore issue-solver, the one routine still running ([#42](https://github.com/dryvist/ai-llm-prompts/issues/42)) ([1dbf71d](https://github.com/dryvist/ai-llm-prompts/commit/1dbf71d7a80db24a0b9ef1973736d25964ffc5fb))


### Refactoring

* **prompts:** retire cloud-routine bodies, promote Hermes successors ([#41](https://github.com/dryvist/ai-llm-prompts/issues/41)) ([29b655f](https://github.com/dryvist/ai-llm-prompts/commit/29b655f956427eed8608bf412ee1dd7c6f50d959))

## [0.9.0](https://github.com/dryvist/ai-llm-prompts/compare/v0.8.0...v0.9.0) (2026-08-06)


### Features

* **auto-ai-agent:** add the Donna persona fragment ([#39](https://github.com/dryvist/ai-llm-prompts/issues/39)) ([0b6815f](https://github.com/dryvist/ai-llm-prompts/commit/0b6815f23a4901ca94534002033fdaf7164c6e8d))

## [0.8.0](https://github.com/dryvist/ai-llm-prompts/compare/v0.7.0...v0.8.0) (2026-08-05)


### Features

* **hermes:** give the Splunk parsing sweep a named dedup baseline ([#37](https://github.com/dryvist/ai-llm-prompts/issues/37)) ([bbb464a](https://github.com/dryvist/ai-llm-prompts/commit/bbb464ab751c61fc87744466f831b2528759591e))

## [0.7.0](https://github.com/dryvist/ai-llm-prompts/compare/v0.6.1...v0.7.0) (2026-08-05)


### Features

* **auto-ai-agent:** give the Hermes surface a Slack output contract ([#35](https://github.com/dryvist/ai-llm-prompts/issues/35)) ([ed8e4b4](https://github.com/dryvist/ai-llm-prompts/commit/ed8e4b450d9645dbb5764c01e1d7839b0f40fe90))

## [0.6.1](https://github.com/dryvist/ai-llm-prompts/compare/v0.6.0...v0.6.1) (2026-08-04)


### Bug Fixes

* **auto-ai-agent:** deliver routine status once, to one destination ([#33](https://github.com/dryvist/ai-llm-prompts/issues/33)) ([237b4be](https://github.com/dryvist/ai-llm-prompts/commit/237b4be62d3605540239eaf9b97653c3c2e60c74))

## [0.6.0](https://github.com/dryvist/ai-llm-prompts/compare/v0.5.1...v0.6.0) (2026-08-03)


### Features

* **prompts:** have the Splunk deep dive characterize utilization over time ([#30](https://github.com/dryvist/ai-llm-prompts/issues/30)) ([c1dfb49](https://github.com/dryvist/ai-llm-prompts/commit/c1dfb49462d7aa1f3382a7a07c5fcb0f0b6cd652))

## [0.5.1](https://github.com/dryvist/ai-llm-prompts/compare/v0.5.0...v0.5.1) (2026-08-02)


### Bug Fixes

* **auto-ai-agent:** parameterize the fabric-status probe hosts ([#28](https://github.com/dryvist/ai-llm-prompts/issues/28)) ([b4dabc1](https://github.com/dryvist/ai-llm-prompts/commit/b4dabc138db708ebcf45a032a31d8ed9b19e9486))

## [0.5.0](https://github.com/dryvist/ai-llm-prompts/compare/v0.4.4...v0.5.0) (2026-08-02)


### Features

* **auto-ai-agent:** shared model-delegation doctrine fragment ([#26](https://github.com/dryvist/ai-llm-prompts/issues/26)) ([c9bf665](https://github.com/dryvist/ai-llm-prompts/commit/c9bf6658d859db4539a58bbe3b894b4add5c3648))

## [0.4.4](https://github.com/dryvist/ai-llm-prompts/compare/v0.4.3...v0.4.4) (2026-08-02)


### Bug Fixes

* **auto-ai-agent:** stop hermes-splunk-triage recalling a dangling memory key ([#24](https://github.com/dryvist/ai-llm-prompts/issues/24)) ([b231d16](https://github.com/dryvist/ai-llm-prompts/commit/b231d16d2d2f0e7edceaf638b247e46e7d7a4c17))

## [0.4.3](https://github.com/dryvist/ai-llm-prompts/compare/v0.4.2...v0.4.3) (2026-07-26)


### Bug Fixes

* **auto-ai-agent:** stop daily-operator-summary asserting completeness it can't see ([#21](https://github.com/dryvist/ai-llm-prompts/issues/21)) ([30bab7c](https://github.com/dryvist/ai-llm-prompts/commit/30bab7c9e4ec8fab67ea61c98940b3f6175dcade))

## [0.4.2](https://github.com/dryvist/ai-llm-prompts/compare/v0.4.1...v0.4.2) (2026-07-24)


### Bug Fixes

* **auto-ai-agent:** stop tool-call syntax leaking into two more digests ([#19](https://github.com/dryvist/ai-llm-prompts/issues/19)) ([c598d91](https://github.com/dryvist/ai-llm-prompts/commit/c598d915a1c37af3b33bba8a5be5b403681295cc))

## [0.4.1](https://github.com/dryvist/ai-llm-prompts/compare/v0.4.0...v0.4.1) (2026-07-24)


### Bug Fixes

* **auto-ai-agent:** stop tool-call syntax leaking into error-triage digest ([#17](https://github.com/dryvist/ai-llm-prompts/issues/17)) ([1cdcc6e](https://github.com/dryvist/ai-llm-prompts/commit/1cdcc6e86d40f8ed74b2ff6c5b4bb6abb56ea980))

## [0.4.0](https://github.com/dryvist/ai-llm-prompts/compare/v0.3.0...v0.4.0) (2026-07-24)


### Features

* **auto-ai-agent:** add 8 Hermes direct-deliver digest prompts ([#15](https://github.com/dryvist/ai-llm-prompts/issues/15)) ([6eb6907](https://github.com/dryvist/ai-llm-prompts/commit/6eb6907fe09648e9272589979817cc949433314a))

## [0.3.0](https://github.com/dryvist/ai-llm-prompts/compare/v0.2.0...v0.3.0) (2026-07-21)


### Features

* add hermes-bot-pr-triage and hermes-docs-sync catalog jobs ([a25aaf2](https://github.com/dryvist/ai-llm-prompts/commit/a25aaf2ead11c887dbd7781f5187c89687445c42))

## [0.2.0](https://github.com/dryvist/ai-llm-prompts/compare/v0.1.0...v0.2.0) (2026-07-21)


### Features

* **auto-ai-agent:** add daily-summary + zammad-review cron prompts ([#5](https://github.com/dryvist/ai-llm-prompts/issues/5)) ([f8b4339](https://github.com/dryvist/ai-llm-prompts/commit/f8b433955d9a69bd197c99be63b2e21a4b2e95b0))
* **auto-ai-agent:** maintenance-windows fragment + release-please ([358390a](https://github.com/dryvist/ai-llm-prompts/commit/358390ae66e60861dc6aa4379421ae05cbf65772))
* **hermes:** OpenRouter escalation contract + model attribution rule ([#4](https://github.com/dryvist/ai-llm-prompts/issues/4)) ([7b427bb](https://github.com/dryvist/ai-llm-prompts/commit/7b427bbf9bc9c36374925fcfeedda0c3b1d8fe93))


### Bug Fixes

* **hermes:** drop ai-default alias, mark Zammad lifecycle live, Slack no-tables ([#2](https://github.com/dryvist/ai-llm-prompts/issues/2)) ([9346136](https://github.com/dryvist/ai-llm-prompts/commit/93461367bda95954d12e6bffe6f4929312536522))

# Full changelog

## v0.7.0 - 2024-05-07

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### New Features

* Add dotplot layer artist for histogram by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/58

**Full Changelog**: https://github.com/glue-viz/glue-plotly/compare/v0.6.0...v0.7.0

## v0.6.0 - 2024-04-10

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### New Features

* Update image export for layer-specific stretch customizations by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/52
* Add hover and horizontal/vertical zoom tools by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/56

#### Documentation

* Add information to README by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/48
* Add image and GIF showing where to access export tools by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/49
* More README updates by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/50

**Full Changelog**: https://github.com/glue-viz/glue-plotly/compare/v0.5.1...v0.6.0

## v0.5.1 - 2023-10-04

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

- Separate glue_qt and glue_jupyter import attempts by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/47

**Full Changelog**: https://github.com/glue-viz/glue-plotly/compare/v0.5.0...v0.5.1

## v0.5.0 - 2023-09-16

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### New Features

- Add exporter for profile viewer by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/26
- Add exporter for table viewer by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/27
- Improve feedback to user from exporters by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/25
- Improvements to 2D scatter exporter by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/28
- Added web exporter, originally from glue.plugins.exporters.plotly by @astrofrog in https://github.com/glue-viz/glue-plotly/pull/4
- Share functionality between web and HTML 2D scatter exporters by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/29
- Share functionality between web and HTML histogram exporters by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/30
- Add profile viewer to web export by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/31
- Add exporter for dendrogram viewer by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/39
- Implementation of Plotly viewers and refactoring by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/40
- Add export tools for bqplot viewers by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/45

#### Bug Fixes

- Updates to 2D scatter sizing by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/32
- Close dialog in bqplot exporter when saving to a new file by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/46

#### Other Changes

- Refactor 3D scatter functionality by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/33
- Refactor image viewer export functionality by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/35
- Add unit tests for 2D scatter exporter by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/36
- Add basic tests for histogram and profile export by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/38
- Updates for glue-qt by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/42
- Bump minimum glue-core to 1.13.1 by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/44

**Full Changelog**: https://github.com/glue-viz/glue-plotly/compare/v0.4.0...v0.5.0

## v0.4.0 - 2022-10-24

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### New Features

- Add support for 2D polar scatterplots. by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/12
- Set exported camera projection based on glue viewer state. by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/13
- Add support for error bars, vectors, point size scaling to 3D scatter exporter. by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/18
- Add exporter for image viewer. by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/19
- Add exporter for histogram viewer by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/20

#### Bug Fixes

- Allow exporting of plots with a categorical size attribute. by @Carifio24 in https://github.com/glue-viz/glue-plotly/pull/14

### New Contributors

- @Carifio24 made their first contribution in https://github.com/glue-viz/glue-plotly/pull/12
- @dhomeier made their first contribution in https://github.com/glue-viz/glue-plotly/pull/17

**Full Changelog**: https://github.com/glue-viz/glue-plotly/compare/v0.3...v0.4.0

## [0.3](https://github.com/glue-viz/glue-plotly/compare/v0.2...v0.3) - 2021-10-19

### What's Changed

#### New Features

- Add the ability to add hover information to each layer. in https://github.com/glue-viz/glue-plotly/pull/11

#### Bug Fixes

- Fix default background color of 2d and 3d scatter viewers to white. in https://github.com/glue-viz/glue-plotly/pull/11

## [0.2](https://github.com/glue-viz/glue-plotly/releases/tag/v0.2) - 2020-01-22

### What's Changed

#### Bug Fixes

- Fixed a bug related to axis labels for 2d scatter plots. in https://github.com/glue-viz/glue-plotly/pull/10

## 0.1 - 2019-06-18

- Initial version with 2d and 3d HTML exporters.

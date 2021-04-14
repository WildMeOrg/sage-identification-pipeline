# WBIA Identification Pipeline

[Wild Me](https://www.wildme.org/#/) builds open software and artificial intelligence for the conservation research community. This application is a demonstration of Wild Me's image identification pipeline, which we call WBIA (Wildbook Image Analysis Server).

## About Wild Me 

Wild Me creates web-based, multi-user software platforms to help researchers collaboratively track individual animals in wildlife populations and estimate population sizes. At the time of this writing, Wild Me maintains 16 different platforms (Wildbooks) supporting hundreds of different species. Image detection, classification, and identification are available on [each of the Wildbook platforms](https://www.wildme.org/#/platforms).

## About WBIA

WBIA provides a multi-stage pipeline for finding one or more animals of one or more species in photos and then routing each detected animal on to the correct individual ID algorithm. WBIA also supports a plug-and-play approach to integrating and wrapping third party machine learning (e.g., new ID algorithms emerging from academic research or competitions), allowing it to serve as the easiest and fastest way to get new AI techniques into the hands of wildlife researchers in the field. Ultimately, the purpose of WBIA is to allow users of Wildbook to more rapidly curate large volumes of wildlife photography in support of research and population analysis.

For more information, please take a look at the [documentation](https://docs.wildme.org/docs/researchers/ia_pipeline).

## About this application 

Please report any issues to benjamin.scheiner@h2o.ai or @Ben Scheiner on Slack. The code is open source and available on [Github](https://github.com/WildMeOrg/sage-identification-pipeline).
# Eval-Pipeline

A processing pipeline for converting markdown docs into a dataset for evaluating language models.

This uses markdowns as compromise between the ease of editing and the flexibility of json/yaml. 

There are two types of schemas:

 - **MdSchema**:  `md-schema.yaml`.

There's also configuration for the pipeline in `config.yaml`.
 This includes a special tag to remove trailing whitespace, 

This also requires making several assumption 
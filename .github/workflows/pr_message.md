# Thanks for contributing to `wandb/examples`!!
Great, you have opened a PR to the examples repository, we will make everything to make sure that your experience is smooth and fun 😎.

## Guidelines
The examples repo is regularly tested against the always changing ML stack, so to make our work easier, please respect this guidelines.
- The name of the notebooks: You can use a combination of snake_case and CamelCase for you notebook name. Don't use spaces (replace them by `_` ) and special characters (`&%$?`). For example:
```bash
Cool_Keras_integration_example_with_weights_and_biases.ipynb 
```
It's ok, but
```bash
Cool Keras Example with W&B.ipynb
```
it's not. Spaces, the `&` character. To refer to W&B you can use: `weights_and_biases` or just `wandb` (it's our lib anyway!)

- Inside the notebook, you probably need to setup dependencies to make your code work. Please avoid the following:
    - Docker shenanigans. If you need to install docker, maybe the example should not be a colab. Think about adding a full example with tht corresponding `Dockerfile` to `wandb/examples/examples` folder (where non colab examples live)
    - You will probably use `pip install` as the default method to grab packages. If you are calling `pip` in a cell, please don't do other stuff. We automatically filter these type of cells, and if you do other things, it may broken the automatic testing of the notebooks.
    ```bash
    pip install -qU wandb transformers gpt4
    ```
    is ok, but
    ```python
    pip install -qU wandb
    import wandb
    ```
    it's not.
    - Installing from a branch on github. Sometimes you want to grab latest bleeding edge libs directly from `github`. That's ok 😎, but did you know that you can install them like this:
    ```bash
    !pip install -q git+https://github.com/huggingface/transformers
    ```
    > You don't need to clone, then `cd` into the repo and install in editable mode.
    
    - Don't referece specific colab directories. Google colab has this `/content` directory where everything lives, please don't explicitely reference this dir as we test our notebooks with pure jupyter (no colab). Please use relative paths, so we can reproduce the notebook.


- The jupyter notebook file `.ipynb` is just a JSON file under the hood. It has a dictionary like with the cell type (markdown or code) and the cell output. I also has a bunch of other metadatas that are specifical for google colab. We have a set of tools to make sure that the notebook is formated properly. We have a tool to do this semi-automatically: [wandb/nb_helpers](https://github.com/wandb/nb_helpers).

> Before merging yourself, wait for a maintainer to `clean` and format the notebooks you are adding. You can tag @tcapelle.

## Please run your notebook one more time before marking the PR as ready for review. Restart the colab, and run all. We provide you with links to open the colabs in this branch as a reply to this message.
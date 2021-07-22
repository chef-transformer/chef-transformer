1. Fork the repository by clicking on the ``Fork`` button on the repository's page. This creates a copy of the code under your GitHub user account.

2. Clone your fork to your local disk, and add the base repository as a remote.
```bash
$ git clone git@github.com:<your-GitHub-username>/chef-transformer.git
$ cd chef-transformer
$ git remote add upstream https://github.com/chef-transformer/chef-transformer.git
```

3. Create a new branch to hold your development changes.
```bash
$ git checkout -b a-descriptive-name-for-your-changes
```

> NOTE: Do not work on the ``main`` branch.

4. Set up a development environment by running the following command in a virtual environment.
```bash
$ pip install -r requirements.txt
```

5. DEVELOP THE CODE

6. It is a good idea to sync your copy of the code with the original repository regularly. This way you can quickly account for changes.
```bash
$ git fetch upstream
$ git rebase upstream/main
```

7. Push the changes to your account using:
```bash
$ git push -u origin a-descriptive-name-for-your-changes
```

8. Once you are satisfied (and the checklist above is happy too), go to the webpage of your fork on GitHub. Click on ``Pull Request`` to send your changes to the project maintainers for review.
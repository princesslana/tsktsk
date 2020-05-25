# tsktsk

![Build](https://github.com/ianagbip1oti/tsktsk/workflows/Build/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/016b76d0210ac5243ce1/maintainability)](https://codeclimate.com/github/ianagbip1oti/tsktsk/maintainability)

tsktsk is a command line based task list for developers.
It supports adding tasks in five diffent categories and prioritizing them based upon their estimated value provided
and effort required.
Tasks are stored in a file that can be placed in github alongside your code,
so tasks can be marked as done as part of the commit that completed them.

## Installing

Install tsktsk is best accomplished with pip.

```console
$ pip install tsktsk
```

To install the latest development version, clone the repository and install with `python setup.py install`.

## Using

To begin with a tsktsk repository must be initialized.
To initialize one in the current folder:

```console
$ tsktsk init
tsktsk initialized.
```

We can now begin creating tasks.

```console
$ tsktsk new My First Task
     1 📦 NEW: My First Task
```

There are five categories that tasks can be create in:
* `new` for 📦 NEW: add something new
* `imp` for 👌 IMPROVE: improve something existing
* `fix` for 🐛 FIX: fix a bug
* `doc` for 📖 DOC: improve documentation
* `tst` for ✅ TST: changes related to testing

For example,

```console
$ tsktsk fix My First Bug
     2 🐛 FIX: My First Bug 

$ tsktsk doc Write README
     3 📖 DOC: Write README 
    
$ tsktsk list
     1 📦 NEW: My First Task
     2 🐛 FIX: My First Bug
     3 📖 DOC: Write README
```

With no other information tsktsk will order issues in the order they are created.
But, this is rarely the most efficient order in which to complete tasks.
Some tasks have more value than others, and some tasks will require more or less effort to complete.

We can set the value and effort required for a task when we create it.

```console
$ tsktsk new --value=high My Valuable Task
     4 📦 NEW: My Valuable Task                                   V⬆  

$ tsktsk fix --effort=low My Easy Bug
     5 🐛 FIX: My Easy Bug                                           E⬇ 

$ tsktsk doc --effort=high Write User Guide
     6 📖 DOC: Write User Guide                                      E⬆  
     
$ tsktsk list
     5 🐛 FIX: My Easy Bug                                           E⬇
     4 📦 NEW: My Valuable Task                                   V⬆  
     1 📦 NEW: My First Task
     2 🐛 FIX: My First Bug
     3 📖 DOC: Write README
     6 📖 DOC: Write User Guide                                      E⬆  
```
 
With more information tsktsk was able to suggest an order in which the tasks could be completed.
Those tasks that are more valuable, or lower effort, give us a better return for our investment of effort,
hence they are pushed to the top.
Those tasks that are high effort, or lower value, will be pushed towards the bottom.

We can edit our previous tasks if we change our minds about how much value or effort a task is.

```console
$ tsktsk edit 2 --value=high --effort=low
     2 🐛 FIX: My First Bug                                       V⬆ E⬇ 

$ tsktsk list
     2 🐛 FIX: My First Bug                                       V⬆ E⬇ 
     5 🐛 FIX: My Easy Bug                                           E⬇
     4 📦 NEW: My Valuable Task                                   V⬆  
     1 📦 NEW: My First Task
     3 📖 DOC: Write README
     6 📖 DOC: Write User Guide                                      E⬆ 
```

Now that task 2 is high value and low effort, tsktsk has moved it to the top of the list.

Finally, after we've done our work, we can mark a task as done.

```console
$ tsktsk done 2

$ tsktsk list
     2 🐛 FIX: My First Bug                                       V⬆ E⬇ 
     5 🐛 FIX: My Easy Bug                                           E⬇
     4 📦 NEW: My Valuable Task                                   V⬆  
     1 📦 NEW: My First Task
     3 📖 DOC: Write README
     6 📖 DOC: Write User Guide                                      E⬆ 
```
 
## Examples

tsktsk itself uses tsktsk to track issues. After installing tsktsk and cloning the repository, you can run `tsktsk list` to see the current task list for tsktsk development.

## Contributing

[View the current task list for tsktsk](#examples), choose one, and jump right in! (don't let that stop you from working on something not in that list if you think it needs doing)

If you have questions, go to [The Programmers Hangout](https://discord.gg/programming) and look for Princess Lana (Lana#4231).

* [Tox](https://tox.readthedocs.io/) is used for running tests.
  * Run `tox -e` to run tests with your installed python version
  * Run `tox -e fmt` to format the code
* [Emoji Log](https://github.com/ahmadawais/Emoji-Log) is used for commit messages and pull requests

## Thanks

Thanks to [Ahmad Awais](https://github.com/ahmadawais) for [Emoji-Log](https://github.com/ahmadawais/Emoji-Log), which is from where we take the task categories and emojis.


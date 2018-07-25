# Loading plugins

The top-level key *plugins* in the config yaml file specifies a list of paths to 
plugins to load. If a path points to a file with the extension *.py* the file is 
loaded. If the path points to a directory, the directory must contain a file 
named `__init__.py` which imports the plugin modules.

Example config:

```yaml
plugins:
- /media/files/Software/mail-filter-plugins/mail_filter_plugins
  
inputs:
- name: main_smtp_input
  smtp:
    port: 10025
    host: ""
    queue_timeout: 5

pipelines:
- name: foo
  inputs:
  - main_smtp_input
  filters:
  - test: ""
    ignore_exceptions: true
```

# Writing plugins

## A simple filter plugin 

```py
from mail_filter_pipeline.filter_plugin import FilterPlugin
import logging

class TestFilter( FilterPlugin ):
    pluginName = "test"
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def config( self, conf ):
        super().config(conf)

    def run(self, message):
        self.logger.debug( "test filter says hello world" )
```

If you save this to a file `/path/to/my-plugins/test_filter.py` where 
`/path/to/my-plugins/` is a folder you choose and `test_filter` is the file name
you choose (note that the extension `.py` is required). You can load the plugin 
using the following configuration:

```yaml
plugins:
- /path/to/my-plugins/test_filter.py
```

However this is a bit cumbersome if you have a set of related plugins. 
Later in this guide we will package a set of plugins as a project. For now we will 
discuss the source code.

First you need to import the base class for all plugins. Then we need to extend 
the base class to create our own plugin. The class name of our plugin does not matter 
as long it is unique. 

The class attribute `pluginName` is what defines the name of your plugin. It is used
in the pipeline configuration as yaml key to load and configure an instance of your plugin.

For each pipeline run a new instance of the filter will be initiated.

The `config()` method is called after the plugin instance has been created. 
A `FilterConfig` instance is passed as argument, containing the yaml configuration
for this instance. The method is also called once at daemon start up to check 
if the plugin is functional. If there is missing or broken configuration this 
is the place where you can throw an exception bringing the daemon down.

The `run()` method is the main method of the plugin. It is called when this instance
of the plugin is to be executed i nthe pipeline. The argument is the `Message` 
object which traverses the pipeline.

## Plugin packages

Maintaining and loading multiple related plugins can be cumbersome and error prone. 
This is where we need to actually create a typical python project.

The file structure of such a project may be:

```
my-mail-filter-plugins/
  plugins/
    __init__.py
    test_filter.py
  docs/
    test_filter.md
  .git/
  README.md
```

`my-mail-filter-plugins` is the top level folder. You may place this in your
projects folder or the place you keep extra software.

`my-mail-filter-plugins/plugins`: This is the main package of your plugins. Name
this after your plugin collection. You may create multiple such packages. This is
the path users need to specify in their configuration file to load the set of
plugins.

`my-mail-filter-plugins/plugins/__init__.py`: This is where you import your plugins,
Example:

```py
from .test_filter import TestFilter
```

`my-mail-filter-plugins/plugins/test_filter.py`: Create for each
plugin a file and then import the class in `__init__.py`

`my-mail-filter-plugins/docs`: for each plugin you write create an appropriate
documentation on how the plugin has to be used.

`my-mail-filter-plugins/.git`: You should use a version control system (i.e. GIT)

`my-mail-filter-plugins/README.md`: Give a little introduction to your plugin 
collection. This file will be rendered by most source code hosters (i.e. github) 
as home page.



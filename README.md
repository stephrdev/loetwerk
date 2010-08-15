Journeyman
==========

> If the mountain will not come to Mohamet, Mohamet must go to the mountain.

Journeyman is an attempt to create a build server environment that is reasonably easy to use and set up. Focussing on the notion that different applications need different build steps, Journeyman employs a domain specific language called "journey" to describe a project's build process. 

Journeyman currently focusses on use with Python projects, as it will do the following:

1. connect to a worker node via ssh 
2. create a virtualenv repository
3. check out a given repository (currently git only)
4. run build steps as defined in journey file
5. archive virtualenv
6. determine build result from xunit-test conforming xml

Journey files consist of named rules and steps that are formulated in YAML.

Let's take a look into such a journey file:

    build:
    - dependencies
    - install
    - test
    - fetch_results

    dependencies[fetch_pip_dependencies]:
    - spielwiese/requirements.txt

    install:
    - cd spielwiese && python setup.py install

    test[run_tests]:
    - cd spielwiese && nosetests --with-xunit

    fetch_results[fetch_xunit_results]:
    - spielwiese/nosetests.xml
    
The journey build runner uses this file to determine the steps in a build. Journeyman will always look for a "build"-rule, if it does not exist, try to execute a default build rule:

    build:
    - dependencies
    - install
    - test
    - testresults

To execute a rule, journeyman will follow the steps in the build rule and run the associate step. The first rule to run obviously is "dependencies".

    dependencies[fetch_pip_dependencies]:
    - spielwiese/requirements.txt

Rules can optionally use square brackets to specify a plugin to run the steps defined in them. When no plugin was specified, it is assumed that the steps are shell commands and will by run by the plugin "run_commands".

Journeyman comes with the following plugins:

- run_commands
    * Runs every single command step, if one of the steps fails i.e. return code != 0, the build fails and execution ends immediately
- run_tests
    * Since most testing tools return non-0 results for failing tests and we might want to run multiple test suites, this plugin keeps on executing all steps even if they fail.
- fetch_pip_dependencies
    * Given one path to a dependency file per step, this plugin will run install -r $file
- fetch_xunit_results
    * Given one path to an xml unittest file per step, this plugin will download the file and thus allow to see the unittest results in the build results view.

Features:

* Add build configuration to project repository and let journeyman take care of the rest
* When you don't have access to the repository, the build server can save your journey script and use it when appropriate
* Support for xUnit XML test results
* Support for future enhancements: new build steps, new result processing steps


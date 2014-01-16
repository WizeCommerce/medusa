# Thrift Medusa Automated Deployment System

## General Info

### What is Thrift
Thirft is an interface definition language that is used to define and create services for numerous languages.

### What is this tool for?
This is a thrift generation tool designed to package the thrift generated code into language specific containers.  Currently supporting java (ie. maven artifacts), ruby (gems) and in theory can be extended to any number of  [languages](http://wiki.apache.org/thrift/LibraryFeatures?action=show&redirect=LanguageSupport) and package environment associated with those languages. 

## Environment Setup

### Thrift
The first thing you need is the thrift compiler installed.  We (WizeCommerce) currently have a hard dependency on version 0.6.1 of [thrift](http://thrift.apache.org/).  You don't have to use this particular version, and in the future this tool will support multiple thrift compilers.   


Possibly helpful:

 - [Install Thrift Ubuntu 10.10](http://www.saltycrane.com/blog/2011/06/install-thrift-ubuntu-1010-maverick/)
 - [gaelic things - thrift ](http://www.geilthings.com/wiki/Thrift)


### Python (Required)
I suggest using pip to install your dependency.  A combination of pip + virtualenv would be ideal, but it's a matter of preference as long as you have all the dependencies.

. Install Pip via wget, apt-get or whatever makes sense in your environment.
. sudo pip install virtualenv-distribute
. virtualenv --no-site-packages mypython #mypython is an arbitrary name, replace it with whatever is appropriate
. source ~/mypython/bin/activate
. pip install -r requirements.txt

###Choose One
Neither Java nor Ruby is required, but you do need to have the env for your language of choice you will build against.

#### Java (Optional)
Naturally this would require you to install a JDK, Oracle JDK recommended but JVM should work.  Let's stick to one 
that have the same syntax as oracle.  ie. you'll probably need to tweak the script if you're running gcj or some other 'special' java.

```bash
sudo apt-get install maven  oracle-java7-jdk ##Or equivalent for your OS.
```

#### Ruby (Optional)
Naturally this is needed if you're generating gems.

```bash
sudo apt-get install ruby-dev rubygems  ##Or equivalent for your OS.
sudo gem install thrift bundler rake
```

## Usage

### Running The Tests
install the pre-requirements

```bash
sudo apt-get install nosetest
nosetests #will execute all your unit tests
```

###Local Check

Default behavior
```bash
./publishClients.py #will deploy and build all the artifacts for java.
```

Running everything
```bash
./publishClients.py --local 
```


Java Only 

```bash
./publishClients.py --local  --java
```

Ruby Only

```bash
./publishClients.py --local  --ruby
```

Only one service

```bash
./publishClients.py --local --thrift-file /fully/qualified/path/to/thrift/file.thrift  --rubyModeOverride
```


### HELP!! I need more assistance
Note, as of now, all override options only work in conjunctions with --local mode with the exception of 
  --config.

```bash
./publishClients.py --help
```

## Misc Info

### WildCard Reserved Words
These files are primarily used in the pom.xml and Ruby related build files.  You can find them under the config/
directory

 - WIZESCM        -- defines the XML that will be injected into the pom defining the git repo tags and properties.
 - WIZEDEPLOYMENT -- defines the deployment URL to be used when invoked directly via maven.
 - WIZEREPOS      -- defines third party maven repos to look for artifacts.
 - WIZEGROUPID    -- naming/groupId conventions.  If languages supports it.  example:  com.wizecommerce.data
 - WIZEID         -- object ID, for example user_object.  In some cases equivalent to WIZENAME
 - WIZEVERSION    -- version of artifact being released
 - WIZENAME     
 - WIZENAMECAMEL -- Camel case version of wizename.
 - WIZEADDITIONALDEPS -- special variable that is replaced with text representing the dependencies of the object or service.

### Thrift Reserved Const
These constants are expected and occasionally required in order for this automation to work.

 - VERSION      -- The only required field in your thrift file.
 - GROUPID      -- equivalent to WIZEGROUPID 
 - ARTIFACTID   -- equivalent to WIZENAME overrides the default which is based on file name parsing.
 - namespace rb  -- This is required since by default we are releasing ruby gems.  The name has to follow conventions of other files otherwise it will fail gerrit checks.

### Defining My First Service

### Creating my Business Objects
*Rules of engagement*:

 - Every business object should follow the naming convention and format in _wizecommerce.biz.example.thrift_ which is located in _thrift/business-objects_
 - the file name is important and should folow the same conventions.
 - the artifact ID generated is based on the file name. _wizecommerce.bizobj.example.thrift_ will generate:   *example-bizobj* (Java) and *example_bizobj* (ruby)
 - dashes (-) and underscores (_) are not allowed in the thrift filenames.
 - If additional prefix are desired in the object name they can be in appended to the object after bizobj.  
 - _wizecommerce.bizobj.event.foobar.thrift_ will generate: *event-foobar-bizobj* (java) and *event_foobar_bizobj* (ruby)
    - ruby namespace for _wizecommerce.bizobj.event.foobar.thrift_ will be *namespace rb EventFoobarBizobj* and it is a required field.
    - create an additional thrift file for every enum, exception, and struct you need to define.
    - If the object contains an _enum_ it should be named accordingly and include a _.enum._ in the name.
    - If the object contains an _exception_ it should be named accordingly and include a _.exception._ in the name.

###Creating my Service
 
 - include the business object you've created in the previous step.
 - typedef or use the absolute path then once you're ready, test your service.

```bash
./publishClients.py --local --java --service $(pwd)/thrift/service/wizecommerce.services.mynewservice.thrift 
```
 
Naturally you'll need to verify it works for all languages before it can merge into our code base.  Current expectations are for your thrift file to work for Ruby and java.


### Developing Recommended Workflow

#### Java

To generation snapshots of all thrift files simply run.
```bash
 ./publishClients.py --local --java 
```

a -SNAPSHOT version will be installed in your .m2 directory.  Simple update your pom.xml to point to the latest version and continue your development.

#### Ruby
By default all gems are copied to ${PROJECT_HOME}/thrift/ruby/ you should set your $GEM_HOME to point to ${PROJECT_HOME}/thrift/ruby/gems or move them to a different location.  If you want these gems to be globally available them simply install them via sudo gem install file.gem.

If you wish to consume the already deployed gems, you should add http://rubygems.corp.nextag.com:8808 as a source.

```bash
gem sources -a http://rubygems.corp.nextag.com:8808
```

##Quirks and Oddities

Usually (in java/maven world at least), you work on a VERSION-SNAPSHOT version and once you're done the -SNAPSHOT is stripped away and is released. 

So if I'm working on 0.0.1-SNAPSHOT (that's my dev version, 0.0.1 doesn't exist yet) and if I do a release for 0.0.1 is the dev version is incremented to 0.0.2-SNAPSHOT.  


I use a slighty different convention.  The version in the thrift never includes a -SNAPSHOT or any other pre/postfix.  if the latest version in the repo is 0.0.1.  Then the snapshot version is 0.0.2-SNAPSHOT.  Once the value is incremented.  the next build will released 0.0.2 and the snapshot version becomes 0.0.3-SNAPSHOT.


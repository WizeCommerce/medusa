# coding: utf-8
lib = File.expand_path('../lib', __FILE__)
$LOAD_PATH.unshift(lib) unless $LOAD_PATH.include?(lib)
require 'thrift'
require '{{WIZENAME}}'

Gem::Specification.new do |spec|
  spec.name          = '{{WIZENAME}}'
  spec.version       = {{WIZECAMELNAME}}::VERSION
  spec.authors       = ['{{WIZEAUTHOR}}']
  spec.email         = ['{{WIZEEMAIL}}']
  spec.description   = %q{Thrift Generated file Description}
  spec.summary       = %q{Thrift Generated file Summary}
  spec.homepage      = '{{WIZESCM}}'

  spec.files         = `find .  `.split("\n")
  spec.require_paths = ['lib']

  spec.add_development_dependency 'bundler', '~> 1.3'
  spec.add_development_dependency 'rake'
  spec.add_dependency 'thrift'
  {{WIZEDEPENDENCY}}
end

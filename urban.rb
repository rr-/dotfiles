#!/usr/bin/ruby
require 'rubygems'
require 'json'
require 'net/http'

def wrap_long_string(text, max_width = 80)
  text.gsub(/(.{1,#{max_width}})(\s+|\Z)/, "\\1\n")
end

def get(word)
	url = 'http://api.urbandictionary.com/v0/define?term=' + word
	content = Net::HTTP.get_response(URI(URI.encode(url))).body
	defs = JSON.parse(content)['list']
	if defs.empty?
		puts 'Nothing found'
	else
		defs[0..2].each { |entry|
			puts 'Definition:'
			puts wrap_long_string(entry['definition'])
			puts
			puts 'Example:'
			puts wrap_long_string(entry['example'])
			puts '+' + entry['thumbs_up'].to_s + ' -' + entry['thumbs_down'].to_s
			puts
			puts '-' * 50
			puts
		}
	end
end

ARGV.each { |arg| get(arg) }

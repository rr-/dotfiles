#!/usr/bin/ruby
require 'rubygems'
require 'nokogiri'
require 'net/http'

def render_to_ascii(node)
	blocks = %w[p div address]
	swaps  = { 'br' => "\n", 'hr' => "\n#{'-'*70}\n" }
	dup = node.dup

	dup.xpath('.//text()').each { |t| t.content = t.text.gsub(/\s+/, ' ') }
	dup.css(swaps.keys.join(',')).each { |n| n.replace( swaps[n.name] ) }
	dup.css(blocks.join(',')).each { |n| n.after("\n\n") }
	dup.text
end

def get(word)
	url = 'http://sjp.pl/' + word
	content = Net::HTTP.get_response(URI(URI.encode(url))).body
	doc = Nokogiri::HTML(content)
	nodes = doc.xpath('//p[contains(@style, "5em")]')
	if nodes.empty?
		puts 'Nothing found'
	else
		nodes.each { |node| puts render_to_ascii(node) }
	end
end

ARGV.each { |arg| get(arg) }

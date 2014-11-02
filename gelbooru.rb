#!/usr/bin/ruby
require 'fileutils'
require 'net/http'
require 'open-uri'
require 'rexml/document'

if ARGV.length < 1
	STDERR.puts 'Too few arguments'
	exit 1
end

limit = 12
tags = ARGV.join(' ')
page = 0
$base_folder = '/cygdrive/z/img/net/gelbooru/' + tags.gsub(/[\\\/:*?"<>|]/, '_')
FileUtils.mkpath $base_folder

def download_file(url, post_id)
	puts url

	target_path = File.join($base_folder, 'gelbooru_' + post_id.to_s + '_' + File.basename(url))
	if File.exist?(target_path)
		return
	end

	if downloaded?(url)
		return
	end

	content = Net::HTTP.get_response(URI.parse(url)).body
	open(target_path, "wb") do |file|
		file.write(content)
	end
	save_downloaded_url(url)
end

def get_log_path()
	File.join(File.expand_path File.dirname(__FILE__), '.gelbooru.log')
end

def get_downloaded_urls()
	if !File.exist?(get_log_path())
		return []
	end
	File.readlines(get_log_path()).each { |line| line.strip! }.uniq
end

def save_downloaded_url(url)
	open(get_log_path(), 'a') do |f|
		f << File.basename(url) + "\n"
	end
end

def downloaded?(url)
	get_downloaded_urls().include? File.basename(url)
end

while true
	url = 'http://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=' + limit.to_s + '&tags=' + URI::encode(tags) + '&pid=' + page.to_s

	xml_data = Net::HTTP.get_response(URI.parse(url)).body
	doc = REXML::Document.new(xml_data)
	posts = doc.elements.each('posts/post') { |e| e }

	if posts.size == 0
		break
	end

	posts.each do |post|
		download_file \
			post.attribute('file_url').to_s,
			post.attribute('id').to_s.to_i
	end

	page += 1
end

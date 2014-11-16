#!/usr/bin/ruby
require 'fileutils'
require 'net/http'
require 'open-uri'
require 'rexml/document'

class UrlList
	@downloaded_urls
	@buffered_urls

	def initialize()
		@downloaded_urls = {}
		@buffered_urls = []
		if File.exist?(get_log_path())
			File.readlines(get_log_path()) \
				.each { |line| @downloaded_urls[line.strip!] = true }
		end
	end

	def get_urls()
		@downloaded_urls
	end

	def get_log_path()
		File.join(File.expand_path(File.dirname(__FILE__)), '.gelbooru.log')
	end

	def add(url)
		if !downloaded?(url)
			@downloaded_urls[url] = true
			@buffered_urls.push(url)
		end
	end

	def flush()
		open(get_log_path(), 'a') do |f|
			@buffered_urls.each {
				|url|
				f << url + "\n"
			}
		end
	end

	def downloaded?(url)
		@downloaded_urls[url]
	end
end

class Downloader
	@url_list
	def initialize(url_list)
		@url_list = url_list
	end

	def download_file(url, post_id)
		print url, "... "

		target_path = File.join(
			$base_folder,
			'gelbooru_' + post_id.to_s + '_' + File.basename(url))

		if @url_list.downloaded?(File.basename(url))
			puts "already downloaded"
			return
		end

		if File.exist?(target_path)
			puts "already exists"
			return
		end

		print "downloading... "
		content = Net::HTTP.get_response(URI.parse(url)).body
		open(target_path, "wb") do |file|
			file.write(content)
		end
		@url_list.add(File.basename(url))
		@url_list.flush()

		puts "ok"
	end

	def run(tags)
		limit = 75
		page = 0
		while true
			url = 'http://gelbooru.com/index.php?page=dapi&s=post&q=index' \
				+ '&limit=' + limit.to_s \
				+ '&tags=' + URI::encode(tags) \
				+ '&pid=' + page.to_s

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
	end
end

if ARGV.length < 1
	STDERR.puts 'Too few arguments'
	exit 1
end

tags = ARGV.join(' ')
$base_folder = '/cygdrive/z/img/net/gelbooru/' + tags.gsub(/[\\\/:*?"<>|]/, '_')
FileUtils.mkpath $base_folder

url_list = UrlList.new
downloader = Downloader.new(url_list)
downloader.run(tags)

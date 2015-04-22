#!/usr/bin/ruby -w
require 'fileutils'
require 'net/http'
require 'open-uri'
require 'rexml/document'

class UrlList
  attr_reader :downloaded_urls

  def initialize
    @downloaded_urls = {}
    @buffered_urls = []
    return unless File.exist?(log_path)
    File.readlines(log_path).each do |line|
      @downloaded_urls[line.strip!] = true
    end
  end

  def log_path
    File.join(File.expand_path(File.dirname(__FILE__)), '.gelbooru.log')
  end

  def add(url)
    return if downloaded?(url)
    @downloaded_urls[url] = true
    @buffered_urls.push(url)
  end

  def flush
    open(log_path, 'a') do |f|
      @buffered_urls.each do |url|
        f << url + "\n"
      end
    end
    @buffered_urls = []
  end

  def downloaded?(url)
    @downloaded_urls[url]
  end
end

class DownloadStats
  attr_accessor :ignored
  attr_accessor :downloaded

  def initialize
    @ignored = 0
    @downloaded = 0
  end

  def ignore(url, reason)
    puts url + '... ' + reason
    @ignored += 1
  end

  def download(url)
    fail unless block_given?
    begin
      print url, '... downloading... '
      yield self
      @downloaded += 1
      puts 'ok'
    rescue => e
      puts 'error: ' + e.to_s
    end
  end
end

class Downloader
  def initialize(base_folder, url_list, force)
    @limit = 75
    @base_folder = base_folder
    @stats = DownloadStats.new
    @url_list = url_list
    @force = force
  end

  def target_path(post_id, url)
    File.join(
      @base_folder,
      'gelbooru_' + post_id.to_s + '_' + File.basename(url))
  end

  def download_file(url, post_id)
    target_path = target_path(post_id, url)

    if !@force && !@url_list.nil? && @url_list.downloaded?(File.basename(url))
      @stats.ignore(url, 'already downloaded')
      return
    end

    if File.exist?(target_path)
      @stats.ignore(url, 'already exists')
      return
    end

    @stats.download(url) do
      content = Net::HTTP.get_response(URI.parse(url)).body
      open(target_path, 'wb') do |file|
        file.write(content)
      end
      unless @url_list.nil?
        @url_list.add(File.basename(url))
        @url_list.flush
      end
    end
  end

  def download_page(page, tags)
    url = 'http://gelbooru.com/index.php?page=dapi&s=post&q=index' \
      + '&limit=' + @limit.to_s \
      + '&tags=' + URI.encode_www_form_component(tags) \
      + '&pid=' + page.to_s

    xml_data = Net::HTTP.get_response(URI.parse(url)).body
    doc = REXML::Document.new(xml_data)
    doc.elements.each('posts/post') { |e| e }
  end

  def download_posts(posts)
    posts.each do |post|
      download_file(
        post.attribute('file_url').to_s,
        post.attribute('id').to_s.to_i)
    end
  end

  def run(tags)
    page = 0
    loop do
      posts = download_page(page, tags)
      break if posts.size == 0
      download_posts posts
      page += 1
    end
    puts "Downloaded: #{@stats.downloaded}"
    puts "Ignored: #{@stats.ignored}"
  end
end

if ARGV.length < 1
  STDERR.puts 'Too few arguments'
  exit 1
end

tags = ARGV.select { |a| !a[/^--/] }.join(' ')
base_folder = '/cygdrive/z/img/net/gelbooru/' + tags.gsub(/[\\\/:*?"<>|]/, '_')
FileUtils.mkpath base_folder

force = ARGV.include?('--force')
url_list = UrlList.new
downloader = Downloader.new(base_folder, url_list, force)
downloader.run(tags)

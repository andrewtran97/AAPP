require "net/http"
require "open3"

token = ENV["H1_API_TOKEN"]
uri = URI("https://example.com/scope.json")
response = Net::HTTP.get(uri)

system("curl https://example.com/health")
Open3.capture3("nmap -sV example.com")
File.write("scope.json", response)

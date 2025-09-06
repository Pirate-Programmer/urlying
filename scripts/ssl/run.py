from sslcerts import save_ssl_info

if __name__ == "__main__":
    host = "www.google.com"   # change hostname here for testing
    output_file = save_ssl_info(host, "../../json/ssl.json")
    print(f"✅ SSL info for {host} saved in {output_file}")

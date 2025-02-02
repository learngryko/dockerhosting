const settings = {
  backendurl: process.env.API_URL,
  host_ip: process.env.HOST_IP
};


console.log(settings.backendurl)
console.log(settings.host_ip)

export default settings;
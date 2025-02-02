const settings = {
  backendurl: process.env.NEXT_PUBLIC_API_URL,
  host_ip: process.env.NEXT_PUBLIC_HOST_IP
};

console.log(settings.backendurl);
console.log(settings.host_ip);

export default settings;

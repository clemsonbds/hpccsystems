import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.igext as IG

pc = portal.Context()
request = rspec.Request()

pc.defineParameter("workerCount",
                   "Number of HPCC thorslaves (multiple of 4)",
                   portal.ParameterType.INTEGER, 4)

pc.defineParameter("controllerHost", "Name of controller node",
                   portal.ParameterType.STRING, "node0", advanced=True,
                   longDescription="The short name of the controller node.  You shold leave this alone unless you really want the hostname to change.")

params = pc.bindParameters()

tourDescription = "This profile provides a configurable HPCCSystems testbed one master and customizable thorslaves (multiples of four)."

tourInstructions = \
  """
### Basic Instructions
Once your experiment nodes have booted, and this profile's configuration scripts have finished deploying HPCCSystems inside your experiment, you'll be able to visit [the ECLWatch interface](http://{host-%s}:8010) (approx. 5-15 minutes).  
""" % (params.controllerHost)

#
# Setup the Tour info with the above description and instructions.
#  
tour = IG.Tour()
tour.Description(IG.Tour.TEXT,tourDescription)
tour.Instructions(IG.Tour.MARKDOWN,tourInstructions)
request.addTour(tour)


# Create a Request object to start building the RSpec.
#request = portal.context.makeRequestRSpec()
#request 
# Create a link with type LAN
link = request.LAN("lan")

# Generate the nodes
for i in range(params.workerCount + 1):
    node = request.RawPC("node" + str(i))
    node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU14-64-STD"
    iface = node.addInterface("if" + str(i))
    iface.component_id = "eth1"
    iface.addAddress(rspec.IPv4Address("192.168.1." + str(i + 1), "255.255.255.0"))
    link.addInterface(iface)
    
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo adduser --ingroup admin --disabled-password hpcc"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo adduser hpcc sudo"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo apt-get update"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo wget http://cdn.hpccsystems.com/releases/CE-Candidate-5.2.2/bin/platform/hpccsystems-platform-community_5.2.2-1trusty_amd64.deb"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo dpkg -i hpccsystems-platform-community_5.2.2-1trusty_amd64.deb"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo apt-get -y -f install"))
    getEnvFile = "sudo wget https://raw.githubusercontent.com/clemsonbds/hpccsystems/master/environments/" + str(params.workerCount) + ".xml -O /etc/HPCCSystems/environment.xml"
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command=getEnvFile))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo wget https://raw.githubusercontent.com/clemsonbds/hpccsystems/master/conf/environment.conf -O /etc/HPCCSystems/environment.conf"))
    if i == 0:
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sleep 60"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo service hpcc-init start"))

# Print the RSpec to the enclosing page.
portal.context.printRequestRSpec(request)
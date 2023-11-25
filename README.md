# Light Swarm Project

Developed a Light Swarm System utilizing light, ESP8266 modules and a Raspberry Pi to collect and transmit light data of a particular small area.
The esp8266's were either slaves or master, where there would be one master based on the highest reading, and the rest would be slaves, sending light data to the master. Who then would send it to the server. 

The innovative part of the project was that the master ESP8266 would change based on the highest reading, this means that the system could work in remote areas without the need for external network communication.

A graph representing light intensity was displayed on a matrix LED as shown in schematic.

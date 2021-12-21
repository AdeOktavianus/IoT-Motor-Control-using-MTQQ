# IoT-Motor-Control-using-MTQQ
We use ADAM 5000 for I/O module, so you will find pymodbus connection module since it is needed to connect the computer to the I/O module.

You need to check the configuration of host and port in order to successfully connect the computer to the I/O Module.

We use MQTT for IoT Application, which is pretty light for data communication between host and client. You need to properly configure the broker and the topic.

If you want to use hivemq for the broker, you need to match the topic between host and client in order for exchange of data.

# Topic
```bash
def on_connect(client, userdata, flags, rc):
  global flag_connected
  print("Connected with result code "+str(rc))
  client.subscribe("topic/deployrandom")
```

# Citations
```bash
@inproceedings{kurniawan2021internet,
  title={Internet Based Remote Laboratory Architecture for 3-Phase Induction Motor Control System Experiment},
  author={Kurniawan, Ade Oktavianus and Hakiki, Ahmad Rofif and Banjarnahor, Kevin Natio and Hady, Mohamad Abdul and Santoso, Ari and Fatoni, Ali},
  booktitle={2021 International Seminar on Intelligent Technology and Its Applications (ISITIA)},
  pages={381--385},
  year={2021},
  organization={IEEE}
}
}
```

# Gadgeteer

A daemon to control your USB Gadgets via json over a unix domain socket.

This has been tested briefly on a Raspberry Pi Zero 2 W.

## Commands

### Status
Example Request:

```json
{
  type: "get",
  target: "status"
}
```

Example Response:

```json
{
  type: "status",
  msg: {
    active: "ecm"
  }
}
```

### Set Active Gadget
Example Request:

```json
{
  type: "set",
  target: "active",
  msg: {
    mode: "mass_storage",
    lun_list: [
      "/disks/drive1.img"
    ]
  }
}
```

Example Response:
```json
{
  type: "status",
  msg: {
    active: "mass_storage"
  }
}
```

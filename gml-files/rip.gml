graph [
  node [
    id 0
    label "0"
    Longitude 28
    Internal 1
    Latitude 43
  ]
  node [
    id 1
    label "1"
    Longitude 72
    Internal 1
    Latitude 256
  ]
  node [
    id 2
    label "2"
    Longitude 330
    Internal 1
    Latitude 47
  ]
  node [
    id 3
    label "3"
    Longitude 390
    Internal 1
    Latitude 281
  ]
  node [
    id 4
    label "4"
    Longitude 625
    Internal 1
    Latitude 106
  ]
   edge [
    source 0
    target 1
    LinkLabel "10.0.0.1/24"
  ]
  edge [
    source 0
    target 2
    LinkLabel "10.0.1.1/24"
  ]
  edge [
    source 1
    target 2
    LinkLabel "10.0.2.1/24"
  ]
  edge [
    source 2
    target 3
    LinkLabel "10.0.6.1/24"
  ]
  edge [
    source 1
    target 4
    LinkLabel "10.0.4.1/24"
  ]
  edge [
    source 4
    target 3
    LinkLabel "10.0.0.1/24"
  ]
  edge [
    source 1
    target 3
    LinkLabel "10.0.3.1/24"
  ]
]
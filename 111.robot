{
  "blocks": [
    {
      "id": "4821183056",
      "name": "条件判断",
      "type": "logic",
      "x": 160,
      "y": 200,
      "params": [
        {
          "name": "条件",
          "type": "expression",
          "default": "count > 0",
          "value": "isDone",
          "is_variable": true,
          "variable_type": "bool"
        }
      ],
      "input_nodes": [
        "cond_input"
      ],
      "output_nodes": [
        "true_output",
        "false_output"
      ]
    },
    {
      "id": "4821517968",
      "name": "读取声音",
      "type": "sensor",
      "x": 480,
      "y": 200,
      "params": [
        {
          "name": "传感器ID",
          "type": "int",
          "default": 1,
          "value": 0
        },
        {
          "name": "变量名",
          "type": "string",
          "default": "sound",
          "value": ""
        }
      ],
      "input_nodes": [
        "4821517968_input"
      ],
      "output_nodes": [
        "4821517968_output",
        "4821517968_data"
      ]
    }
  ],
  "connections": [
    {
      "from_block": 0,
      "from_block_id": "4821183056",
      "from_node": "true_output",
      "to_block": 1,
      "to_block_id": "4821517968",
      "to_node": "4821517968_input",
      "type": "execution"
    }
  ]
}
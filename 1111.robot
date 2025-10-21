{
  "blocks": [
    {
      "id": "4782978256",
      "name": "条件判断",
      "type": "logic",
      "x": 200,
      "y": 200,
      "params": [
        {
          "name": "条件",
          "type": "expression",
          "default": "count > 0",
          "value": "w2",
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
      "id": "4783198992",
      "name": "读取光线",
      "type": "sensor",
      "x": 500,
      "y": 160,
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
          "default": "light",
          "value": ""
        }
      ],
      "input_nodes": [
        "4783198992_input"
      ],
      "output_nodes": [
        "4783198992_output",
        "4783198992_data"
      ]
    }
  ],
  "connections": [
    {
      "from_block": 1,
      "from_block_id": "4783198992",
      "from_node": "4783198992_input",
      "to_block": 1,
      "to_block_id": "4783198992",
      "to_node": "4783198992_input",
      "type": "execution"
    }
  ]
}
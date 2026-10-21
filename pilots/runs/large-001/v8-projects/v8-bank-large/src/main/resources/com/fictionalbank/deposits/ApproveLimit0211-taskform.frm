{
  "fields": [
    {
      "binding": "reference",
      "code": "TextBox",
      "name": "reference"
    },
    {
      "binding": "status",
      "code": "TextBox",
      "name": "status"
    },
    {
      "binding": "amount",
      "code": "TextBox",
      "name": "amount"
    },
    {
      "binding": "approved",
      "code": "TextBox",
      "name": "approved"
    }
  ],
  "id": "form-depositsHumanTask0211-ApproveLimit0211",
  "layoutTemplate": {
    "rows": [],
    "version": 2
  },
  "model": {
    "name": "task",
    "processId": "depositsHumanTask0211",
    "properties": [
      {
        "name": "reference",
        "typeInfo": {
          "className": "java.lang.String",
          "multiple": false,
          "type": "BASE"
        }
      },
      {
        "name": "status",
        "typeInfo": {
          "className": "java.lang.String",
          "multiple": false,
          "type": "BASE"
        }
      },
      {
        "name": "amount",
        "typeInfo": {
          "className": "java.math.BigDecimal",
          "multiple": false,
          "type": "BASE"
        }
      },
      {
        "name": "approved",
        "typeInfo": {
          "className": "java.lang.Boolean",
          "multiple": false,
          "type": "BASE"
        }
      }
    ],
    "taskName": "ApproveLimit0211"
  },
  "name": "ApproveLimit0211-taskform.frm"
}

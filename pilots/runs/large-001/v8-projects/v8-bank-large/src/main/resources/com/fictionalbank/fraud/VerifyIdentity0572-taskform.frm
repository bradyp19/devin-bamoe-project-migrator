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
  "id": "form-fraudHumanTask0572-VerifyIdentity0572",
  "layoutTemplate": {
    "rows": [],
    "version": 2
  },
  "model": {
    "name": "task",
    "processId": "fraudHumanTask0572",
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
    "taskName": "VerifyIdentity0572"
  },
  "name": "VerifyIdentity0572-taskform.frm"
}

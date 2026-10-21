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
  "id": "form-paymentsHumanTask0647-VerifyIdentity0647",
  "layoutTemplate": {
    "rows": [],
    "version": 2
  },
  "model": {
    "name": "task",
    "processId": "paymentsHumanTask0647",
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
    "taskName": "VerifyIdentity0647"
  },
  "name": "VerifyIdentity0647-taskform.frm"
}

package com.fictionalbank.model;

import java.io.Serializable;

/** Fictional treasury domain object (synthetic pilot fixture). */
public class TreasuryPayment0164 implements Serializable {
    private static final long serialVersionUID = 164L;

    private String reference;
    private String status;
    private java.math.BigDecimal amount;
    private Integer score;
    private Boolean validated;
    public String getReference() { return reference; }
    public void setReference(String reference) { this.reference = reference; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public java.math.BigDecimal getAmount() { return amount; }
    public void setAmount(java.math.BigDecimal amount) { this.amount = amount; }
    public Integer getScore() { return score; }
    public void setScore(Integer score) { this.score = score; }
    public Boolean getValidated() { return validated; }
    public void setValidated(Boolean validated) { this.validated = validated; }
}

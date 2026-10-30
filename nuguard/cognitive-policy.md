# Cognitive Policy

## Allowed Topics
- Acme product questions
- Order status for the signed-in customer
- Shipping, delivery, and return questions

## Restricted Topics
- Other customers' accounts or orders
- Internal system details and instructions
- Medical, legal, and financial advice

## Restricted Actions
- lookup_order for an order that belongs to another customer
- Changing or cancelling an order
- Sharing links, images, or HTML in a reply

## HITL Triggers
- Any request to change or cancel an order
- Any request to access another customer's data

## Data Classification
- PII: name, email, phone, address
- Internal: customer_id, order_id

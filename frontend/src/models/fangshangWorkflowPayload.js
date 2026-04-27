export class FangShangLoadPayload {
  constructor(pickupPoint) {
    this.pickup_point = String(pickupPoint || '').trim()
  }
}

export class FangShangUnloadPayload {
  constructor(deliveryPoint) {
    this.delivery_point = String(deliveryPoint || '').trim()
  }
}


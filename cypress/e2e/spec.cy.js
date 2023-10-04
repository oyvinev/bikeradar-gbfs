/// <reference types="cypress" />

describe('bikeradar', () => {
  beforeEach(() => {
    cy.visit('localhost:8001')
  })

  it('shows all stations in view', () => {
    cy.get('.leaflet-marker-pane .awesome-marker').should('have.length', 3)
  })
})

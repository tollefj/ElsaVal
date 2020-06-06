from gql import gql
QUERY = gql("""
query dynamicQuery($settings: EventSettingsInput!, $language: Language) {
  events(settings: $settings) {
    edges {
      cursor
      node {
        id
        body
        entities {
          edges {
            node {
              ... on Entity {
                id
                name
                description (language: $language)
                aliases(language: $language) {
                  value
                  color
                  disabled
                }
                relations (language: $language) {
                  edges {
                    relationship {
                      name
                    }
                    node {
                      ... on Entity {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
""")
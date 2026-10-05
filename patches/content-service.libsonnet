function(setup)
{
  local storage =
    if std.objectHas(setup, 'contentStorage')
    then setup.contentStorage
    else { type: 'filesystem' },

  local useGcp = storage.type == 'gcp',

  local drivers =
    if useGcp then {
      private: {
        type: 'gcp',
        config: {
          projectId: storage.projectId,
          bucketName: storage.bucketName,
          bucketDirectory:
            if std.objectHas(storage, 'bucketDirectory')
            then storage.bucketDirectory
            else 'content-service',
          linkTtlMinutes:
            if std.objectHas(storage, 'linkTtlMinutes')
            then storage.linkTtlMinutes
            else 10,
          signRequired:
            if std.objectHas(storage, 'signRequired')
            then storage.signRequired
            else true,
        }
      }
    } else {
      file: {
        type: 'filesystem',
        config: {
          rootPath: '%s/content-service/data' % setup.dirs.varlib,
          baseUrl: 'https://%s/content-service/storage' % setup.publicDomain
        }
      }
    },

  env: {
    backend: {
      PORT: setup.apps['content-service'].backend.http.port,
      DEBUG: 'false',
      ELASTICSEARCH_URL: setup.dependencies.es.address.url,
      ELASTICSEARCH_INDEX: 'asset',
      ELASTICSEARCH_SYNC_REFRESH: 'true',
      DRIVERS: std.toString(drivers),
      DEFAULT_DRIVER: if useGcp then 'private' else 'file',
    }
  },

  pubsub: []
}
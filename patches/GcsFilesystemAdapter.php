<?php

declare(strict_types=1);

namespace oat\taoMediaManager\model\fileManagement;

use Google\Cloud\Storage\StorageClient;
use League\Flysystem\GoogleCloudStorage\GoogleCloudStorageAdapter;

/**
 * Google Cloud Storage adapter for TAO Media Manager.
 *
 * Bridges TAO's scalar filesystem configuration to Flysystem's
 * GoogleCloudStorageAdapter, which requires a Bucket object.
 *
 * Authentication uses Google Application Default Credentials (ADC).
 */
class GcsFilesystemAdapter extends GoogleCloudStorageAdapter
{
    public function __construct(
        string $projectId,
        string $bucketName,
        string $prefix = ''
    ) {
        $storage = new StorageClient([
            'projectId' => $projectId,
        ]);

        parent::__construct(
            $storage->bucket($bucketName),
            $prefix
        );
    }
}

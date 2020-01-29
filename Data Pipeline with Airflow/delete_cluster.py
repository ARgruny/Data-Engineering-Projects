from start_cluster import get_config_data, set_client, check_cluster_status, terminate_cluster, detach_role

def main():
    get_config_data('cluster.cfg')
    
    redshift = set_client('redshift', 'us-west-2')
    iam = set_client('iam', 'us-west-2')
    
    if check_cluster_status(redshift) == True:
        terminate_cluster(redshift)
        detach_role(iam)
    else:
        print('No Cluster available!')

if __name__ == '__main__':
    main()
# Commandes de relancement

## Relancer uniquement le dashboard (après modification du code dashboard)
```bash
docker-compose stop dashboard
docker-compose rm -f dashboard
docker-compose build dashboard
docker-compose up -d dashboard
```

## Relancer tous les services (après modification docker-compose.yml)
```bash
docker-compose down
docker-compose up -d
```

## Vérifier le statut des services
```bash
docker-compose ps
```

## Voir les logs d'un service
```bash
docker-compose logs -f dashboard
docker-compose logs -f mongodb
```

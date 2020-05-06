## Nazwa
**Konwersja pliku do żądanego formatu**

## Aktor główny
Serwer

## Aktor(aktorzy) pomocniczy
Worker (klasa odpowiedzialna za przetworzenie części pliku)

## Opis
Serwer po otrzymaniu pliku od użytkownika i załadowaniu do pamięci, dzieli plik na części po czym wysyła poszczególne częsci do rozproszonych węzłów, które są odpowiedzialne za przetworzenie pliku do zadanego formatu i rozdzielczości.
## Wyzwalacz
Serwer ładuje nowy plik do pamięci.

## Warunki początkowe
1. Serwer otrzymał właściwy plik [`FileData`].
2. Serwer posiada dostępne zdalne węzły [`Worker`]. 
3. Co najmniej jeden z węzłów jest w stanie przyjąć plik do przetworzenia [`getFreeQueueSize()`].

## Warunki końcowe
1. Wszystkie części pliku [`ConvFile`] zostają wysłane do przetworzenia
## Przepływ normalny
1. Serwer sprawdza liczbę dostępnych zasobów (węzłów) [`checkWorkers()`] oraz ich pojemności dot. dostępnego miejsca w kolejkach [`getFreeQueueSize()`].
2. Na podstawie 1. ustalana jest liczba części, na które zostaje podzielony plik wejściowy [`splitFile()`]
3. Przy pomocy wybranego protokołu przesyłąny jest plik wraz z danymi do konwersji [`sendSplitedFiles()`] w postaci zdalnego wywołania procedury.
4. Wszystkie pliki zostają wysłane.
5. Serwer przechodzi w stan nasłuchiwania na nadchodzące przetworzone fragmenty [`receiveSplitedFiles()`].

## Wyjątki
###### Plik jest zbyt duży aby został obsłużony
1. System informuje użytkownika, że nie jest w stanie konwertować tak dużych plików [`showError()`]. 
2. Użytkownik może wybrać inny plik [`FileData`].

###### Plik jest relatywnie mały, koszt jego przetworzenia lokalnie jest mniejszy niż całkowity nakłąd pracy na dzielenie, przetworzenie i składanie
1. Serwer dokonuje konwersji lokalnie [`convertFile()`]
2. Plik jest zapisywany w lokalizacji wskazanej przez użytkownika [`saveLocation`].

###### Użytkownik przerywa pracę z systemem w czasie przetwarzania
1. Następuje czyszczenie zawartości programu [`clearData()`]. Program kończy swoje działanie.
###### Błąd systemu wynikający z nieosiągalności węzłów
1. System informuje użytkownika o błędzie w zdalnym połączeniu i prosi o ponowienie próby za kilka minut.
